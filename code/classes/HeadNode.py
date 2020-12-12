import numpy as np
import logging
import random
import mpi4py
mpi4py.rc.recv_mprobe = False
from mpi4py import MPI
from TimeIt import timeit

from HeadGraph import HeadGraph
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES

comm = MPI.COMM_WORLD

# add function names here that needs timing
func_to_time = ["run", "stitch"]
timer = {func:0 for func in func_to_time}
counter = {func:0 for func in func_to_time}


class HeadNode:
    def __init__(self, rank, n_nodes, scale_factor, total_vertices, out_v,
                 out_e, stitch=True, ring_stitch=True, connectivity=0.1):
        """
        Head node for the graph scaler that creates the resulting graph and
        keeps track of what works needs to be done.

        rank: rank inside MPI, system only supports headnode to the rank 0
        n_nodes: number of nodes in the mpi system
        scale_factor: factor the original graph needs to be scaled too
        total_vertices: num vertices in the original graph
        out_v: output file for vertices
        out_e: output file for edges
        stitch: boolean whether or not it need to stitch
        ring_stitch: boolean whether to stitch in ring (True) or random (False)
        connectivity: percentages of vertices that gets edge when stitching.
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.total_vertices = total_vertices
        self.need_stitch = stitch
        self.connectivity = connectivity
        self.ring_stitch = ring_stitch

        # Calculates how many samples need to be created to get the scale factor
        if scale_factor <= 0.5:
            self.num_sample = 1
            self.cutoff_vertices = total_vertices * scale_factor
            logging.debug("collecting " + str(self.cutoff_vertices) + " vertices")
            self.upscale = False
        elif 0.5 < scale_factor < 1:
            self.num_sample = 2
            self.cutoff_vertices = total_vertices * (scale_factor / self.num_sample)
            self.upscale = True
        else:
            self.num_sample = np.int(np.floor(scale_factor * 2))
            self.cutoff_vertices = total_vertices * (scale_factor / self.num_sample)
            self.upscale = True

        logging.debug("collecting " + str(self.cutoff_vertices) + " vertices")
        logging.debug("num samples is " + str(self.num_sample))

        self.graph = HeadGraph(total_vertices, self.num_sample, out_e, out_v)
        self.keep_burning = True

    def __del__(self):
        for k, v in timer.items():
            logging.info(f"timer {k} {v:.2f}")

        for k, v in counter.items():
            logging.info(f"counter {k} {v}")

    @timeit(timer=timer, counter=counter)
    def run(self):
        """
        Main run loop for the headnode, loops over samples and while burning a
        sample handles receiving from compute nodes and send to all whether to
        keep burning (CONTINUE), move to next sample (RESET), or shutdown if done (Kill)
        """
        for cur_sample in range(self.num_sample):
            logging.debug(f"entered sampling cur_sample = {cur_sample}")
            while self.keep_burning:
                logging.info(f"sample {cur_sample}/{self.num_sample}, "
                             f"prog: {self.graph.get_num_sample_vertices(cur_sample)/self.cutoff_vertices}")
                tag = MPI_TAG.CONTINUE.value

                for i in range(1, self.num_compute_nodes+1):
                    logging.debug(f"one headnode. receiving from compute node {i}")
                    data = comm.recv(source=i, tag=MPI_TAG.HEARTBEAT.value)
                    logging.debug(data)

                    if tag == MPI_TAG.CONTINUE.value:
                        for [src, dest] in data:
                            self.graph.add_edge(src, dest, cur_sample)
                            if self.done_burning(cur_sample):
                                self.keep_burning = False
                                if cur_sample < self.num_sample - 1:
                                    tag = MPI_TAG.RESET.value
                                else:
                                    tag = MPI_TAG.KILL.value
                                break
                logging.debug("Sending tags " + str(tag) + " | RESET = 4 | KILL = 5 | CONTINUE = 6")

                for i in range(1, self.num_compute_nodes+1):
                    comm.send(None, dest=i, tag=tag)

            self.graph.next_sample()
            self.keep_burning = True

        logging.debug("start stitch")
        self.stitch()
        logging.debug("end stitch")
        self.graph.write2file()
        logging.debug("done writing")

    @timeit(timer=timer, counter=counter)
    def stitch(self):
        """ Controls the stitching algorithms topologie. """
        if not self.need_stitch:
            return
        if self.upscale:
            if self.ring_stitch:
                vertices = self.graph.get_vertices()
                for i in range(self.num_sample):
                    end = np.int(np.ceil(len(vertices[i])*self.connectivity))
                    while end > 10000:
                        self.stitch_sample(vertices[i], vertices[(i+1) % self.num_sample], 10000)
                        end -= 10000
                    self.stitch_sample(vertices[i], vertices[(i+1) % self.num_sample], end)
            else:
                sample = self.graph.get_vertices_as_one()
                end = np.int(np.ceil(len(sample) * self.connectivity))
                while end > 10000:
                    self.stitch_sample(sample, sample, 10000)
                    end -= 10000
                self.stitch_sample(sample, sample, end)
        else:
            sample = self.graph.get_vertices()[0]
            end = np.int(np.ceil(len(sample) * self.connectivity))
            while end > 10000:
                self.stitch_sample(sample, sample, 10000)
                end -= 10000
            self.stitch_sample(sample, sample, end)

    def stitch_sample(self, src_sample, dest_sample, end):
        """
        adds edges form the two samples to to stich the samples together

        src_sample: sample to take first vertices from
        dest_sample: sample to take second vertices from
        end: number of edges to add
        """
        source = random.sample(src_sample, end)
        destination = random.sample(dest_sample, end)
        for (src, dest) in zip(source, destination):
            if src != dest:
                self.graph.add_edge(src, dest, None, 0)

    def done_burning(self, cur_sample):
        """
        Checks if enough vertices have been added for the current samples

        cur_sample: the current sample
        """
        return self.graph.get_num_sample_vertices(cur_sample) >= self.cutoff_vertices
