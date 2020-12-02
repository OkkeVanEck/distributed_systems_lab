# Load packages.
from mpi4py import MPI

# Load classes and functions from own files.
from ComputeNode import ComputeNode
from HeadNode import HeadNode

# Setup globals for each process.
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
DO_LOG=True


def log(message):
    """General function for logging actions if global variable is set."""
    if DO_LOG:
        print(message)


def get_vertex_rank(vertex_id: int) -> int:
    """Function used by ComputeNodes to propagate fires across nodes."""
    return vertex_id % (size - 1) + 1


def run_sim(scale_factor, dataset, tmp_play, tmp_data, tmp_res):
    """
    Entrypoint for starting a halted forst fire simulation.
    Starts up a single HeadNode and multiple compute nodes.
    """

    # Fetch the right datafiles according to rank of process.

    # Startup node process according to rank of process.
    if rank == 0:
        log(f"Starting HeadNode on {rank}..")
        hn = HeadNode(rank, n_nodes, float(scale_factor), total_vertices)
    else:
        log(f"Starting ComputeNode on {rank}..")
        compute_node = ComputeNode(rank, n_nodes)
        compute_node.init_partition(data)
        compute_node.do_tasks()
