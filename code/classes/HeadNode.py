import numpy as np
import itertools
import logging
import threading
import gzip
import time
import random

from TimeIt import timeit
from HeadGraph import HeadGraph
from Enums import MPI_TAG, VertexStatus, SLEEP_TIMES


from mpi4py import MPI
comm = MPI.COMM_WORLD

class HeadNode:
    def __init__(self, rank, n_nodes, scale_factor, total_vertices, out_v, out_e, stitch=True):
        """
        """
        self.rank = rank
        self.num_compute_nodes = n_nodes - 1
        self.total_vertices = total_vertices
        self.need_stitch = stitch
        self.connectivity = 0.1

        # scale factor 1 will be upscale sample that stays the same size
        if scale_factor < 1:
            self.num_sample = 1
            self.cutoff_vertices = total_vertices * scale_factor
            logging.debug("collecting " + str(self.cutoff_vertices) + " vertices")
            self.upscale = False
        else:
            self.num_sample = np.int(np.floor(scale_factor * 2))
            self.cutoff_vertices = total_vertices * (scale_factor / self.num_sample)
            self.upscale = True
        logging.debug("num samples is " + str(self.num_sample))

        self.graph = HeadGraph(total_vertices, self.num_sample, out_e, out_v)
        self.keep_burning = True

        # add function names here that needs timing
        func_to_time = ["run", "stitch"]
        self.timer = {func:0 for func in func_to_time}

    def __del__(self):
        for k, v in self.timer.items():
            logging.info(f"{k} takes {v}s")

    @timeit(timer=self.timer)
    def run(self):
        for cur_sample in range(self.num_sample):
            while self.keep_burning:
                tag = MPI_TAG.CONTINUE.value
                for i in range(1, self.num_compute_nodes+1):
                    logging.debug(f"one headnode. receiving from compute node {i}")
                    data = comm.recv(source=i, tag=MPI_TAG.HEARTBEAT.value)
                    logging.debug(data)
                    if tag == MPI_TAG.CONTINUE.value:
                        kl = 0 # debug
                        for [src, dest] in data:
                            self.graph.add_edge(src, dest, cur_sample)
                            kl += 1 # debug
                            if self.done_burning(cur_sample):
                                self.keep_burning = False
                                if cur_sample < self.num_sample-1:
                                    tag = MPI_TAG.RESET.value
                                    logging.debug(f"time to reset at compute={i} and element {kl}")
                                else:
                                    tag = MPI_TAG.KILL.value
                                    logging.debug(f"time to kill at compute={i} and element {kl}")
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


    @timeit(timer=self.timer)
    def stitch(self):
        if not self.need_stitch:
            return
        if self.upscale:
            stitch_nodes = list()
            for sample in self.graph.get_vertices():
                stitch_nodes.append(
                    np.random.choice(list(sample),
                        size=np.int(np.ceil(len(sample)*self.connectivity)),
                        replace=False
                    )
                )
            for i in range(self.num_sample):
                if stitch_nodes[i].shape[0] < stitch_nodes[(i+1) % self.num_sample].shape[0]:
                    total = stitch_nodes[i].shape[0]
                else:
                    total = stitch_nodes[(i+1) % self.num_sample].shape[0]

                edges = list(itertools.product(stitch_nodes[i], stitch_nodes[(i+1) % self.num_sample]))
                index_edges = np.random.choice(len(edges), size=total, replace=False)
                for j in index_edges:
                    src, dest = edges[j]
                    self.graph.add_edge(src, dest, None, 0)
        else:
            for sample in self.graph.get_vertices():
                len_sample = len(sample)
                for _ in range(np.int(np.ceil(len(sample)*self.connectivity))):
                    src, dest = random.sample(sample,2)
                    if src != dest:
                        self.graph.add_edge(src, dest, None, 0)

    def done_burning(self, cur_sample):
        return self.graph.get_num_sample_vertices(cur_sample) >= self.cutoff_vertices

