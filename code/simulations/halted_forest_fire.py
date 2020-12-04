# Load packages.
from itertools import takewhile, repeat
from mpi4py import MPI
from sys import argv
import os

# Load classes and functions from own files.
from ComputeNode import ComputeNode
# from HeadNode import HeadNode

# Setup globals for each process.
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
DO_LOG = True


def log(message):
    """General function for logging actions if global variable is set."""
    if DO_LOG:
        print(message)


def rawincount(filename):
    """
    Function to count the number of lines in a file efficiently.
    Found on this stack-overflow: https://stackoverflow.com/a/27518377
    """
    f = open(filename, "rb")
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024)
                                     for _ in repeat(None)))
    return sum(buf.count(b"\n") for buf in bufgen)


def get_vertex_rank(vertex_id: int) -> int:
    """Function used by ComputeNodes to propagate fires across nodes."""
    return vertex_id % (size - 1) + 1


def run_sim(scale_factor, dataset, tmp_play, tmp_data, tmp_res):
    """
    Entrypoint for starting a halted forest fire simulation.
    Starts up a single HeadNode and multiple compute nodes.
    """
    if rank == 0:
        # Fetch the total number of vertices in the dataset.
        num_vertices = rawincount(f"{tmp_data}/{dataset}/{dataset}.v")

        # Start a HeadNode.
        log(f"Starting HeadNode on {rank}..")
        out_v = f"{tmp_res}/scaled_graph.v"
        out_e = f"{tmp_res}/scaled_graph.e"
        f = open(out_v, "w")
        f.close()
        f = open(out_e, "w")
        f.close()
        # HeadNode(rank, size - 1, float(scale_factor), num_vertices, out_v, out_e)
    else:
        # Fetch a dataset partition according to the rank of the process.
        # TODO: Load dataset according to rank of process.

        # Start a ComputeNode.
        log(f"Starting ComputeNode on {rank}..")
        # compute_node = ComputeNode(rank, False, n_nodes)
        # compute_node.init_partition(data)
        # compute_node.do_tasks()
