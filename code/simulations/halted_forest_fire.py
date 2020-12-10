# Load packages.
import logging
import sys

from TimeIt import timeit
from itertools import takewhile, repeat
from mpi4py import MPI

# Load classes and functions from own files.
from ComputeNode import ComputeNode
from HeadNode import HeadNode

# Setup globals for each process.
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


def rawincount(filename):
    """
    Function to count the number of lines in a file efficiently.
    Found on this stack-overflow: https://stackoverflow.com/a/27518377
    """
    f = open(filename, "rb")
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024)
                                     for _ in repeat(None)))
    return sum(buf.count(b"\n") for buf in bufgen)

@timeit
def read_partition_file(path_to_partition_file):
    vert_rank_mapping = dict()
    with open(path_to_partition_file, "r") as fp:
        for line in fp:
            vert, machine = list(map(int, line.strip().split(" ")))
            vert_rank_mapping[vert] = machine

    return vert_rank_mapping


@timeit
def run_sim(scale_factor, dataset, do_stitch, ring_stitch, connectivity,
            tmp_play, tmp_data, tmp_res):
    """
    Entrypoint for starting a halted forest fire simulation.
    Starts up a single HeadNode and multiple compute nodes.
    """
    # Setup logging and print to stdout.
    logging.basicConfig(filename=f'{tmp_res}/node-{rank}.log', filemode="w+",
                        format='%(message)s', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    if rank == 0:
        # Fetch the total number of vertices in the dataset.
        num_vertices = rawincount(f"{tmp_data}/{dataset}/{dataset}.v")

        # Start a HeadNode.
        logging.debug(f"Starting HeadNode on {rank}..")
        out_v = f"{tmp_res}/scaled_graph.v"
        out_e = f"{tmp_res}/scaled_graph.e"
        # hn = HeadNode(rank, size, float(scale_factor), num_vertices, out_v,
        #               out_e, do_stitch, ring_stitch, connectivity)
        # hn.run()

        f_v = open(out_v, "w")
        f_e = open(out_e, "w")
        f_v.writelines(["1", "2", "3", "4", "5", "6"])
        f_e.writelines(["1 2", "2 3", "3 4", "4 5", "5 6", "6 1"])
        f_v.close()
        f_e.close()

        logging.debug(f"Done on headnode")
    else:
        # Fetch the set of edges according to the rank of the process and the
        # number of partitions in use.
        path_to_partition_file = f"{tmp_data}/{dataset}/{dataset}-{size - 1}-partitions/node{rank}.p"
        path_to_edge_file = f"{tmp_data}/{dataset}/{dataset}-{size - 1}-partitions/node{rank}.e"
        vert_rank_mapping = read_partition_file(path_to_partition_file)

        # Start a ComputeNode.
        logging.debug(f"Starting ComputeNode on {rank}..")
        # compute_node = ComputeNode(rank, False, size - 1, vert_rank_mapping)
        # compute_node.init_partition(path_to_edge_file)
        # compute_node.do_tasks()
        logging.debug(f"Compute node {rank} done")
