# Load packages.
from mpi4py import MPI

# Load all classes and functions from own files.
from ComputeNode import ComputeNode

# Setup globals for each process.
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


def get_vertex_rank(vertex_id: int) -> int:
    """Function used by ComputeNodes to propagate fires accross nodes."""
    return vertex_id % (size - 1) + 1


def run_sim():
    print(f"\nWOOHOOO, I got Called by {rank}!")
    cn = ComputeNode(rank, 10)
    print(cn)

    # # Parse call arguments for execution.
    # dataset, tmp_play, tmp_data, tmp_res = parse_args()
    #
    # # Set environment variable for triggering logs during execution.
    # os.environ["DEBUG"] = "True"
    #
    # print(f"\nRank: {rank}\n\tDataset: {dataset}\n\tTmp_play: {tmp_play}\n\t"
    #       f"Tmp_data: {tmp_data}\n\t Tmp_res: {tmp_res}\nDebug: "
    #       f"{os.environ['DEBUG']}\n")
    #
    #
    # # TODO: Read arguments from args. (See a job file what is given in what order)
    # # if rank == 0:
    # #     print("init head node")
    # #     # initialize a head node/head node class
    # # else:
    # #     print("init compute node rank: " + str(rank))
    # #     compute_node = ComputeNode(rank, args.n_nodes)
    # #     compute_node.init_partition(args.data)
    # #     compute_node.do_tasks()
