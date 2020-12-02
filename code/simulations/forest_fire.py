import argparse
import sys

from code.classes.ComputeNode import ComputeNode

# TODO: Pass the local variable to each class as an initialization argument. Or
#   maybe set the variable as an environment variable and let every class assume
#   local if env variable is not defined.
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


USAGE_STRING = """
usage -
    mpirun -n num_nodes python3 forest_fire.py [halted|wild] /path/to/data num_nodes

"""


# This function would be stated somewhere. Only used by ComputeNode, but in
# order to keep the program flexible, it is shared as a variable.
def get_vertex_rank(vertex_id: int) -> int:
    return vertex_id % (size - 1) + 1



if __name__ == "__main__":
    # Set variable for local run.

    # TODO: Read arguments from args. (See a job file what is given in what order)
    parser = argparse.ArgumentParser()
    parser.add_argument("wild")
    parser.add_argument("data")
    parser.add_argument("n_nodes")
    args = parser.parse_args()
    if not args.n_nodes.isdigit():
        print(USAGE_STRING)
        print("n_nodes not a digit")
        sys.exit(0)
    if args.wild[0] != "h" and args.wild[0] != "w":
        print(USAGE_STRING)
        print("halted/wild specification missing")
        sys.exit(0)

    fires_wild = True
    if args.wild[0] == "h":
        fires_wild = False

    if rank == 0:
        pass
        # print("init head node")
        # initialize a head node/head node class
    else:
        # print("init compute node rank: " + str(rank)) 
        compute_node = ComputeNode(rank, fires_wild, int(args.n_nodes))
        compute_node.init_partition(args.data)
        compute_node.do_tasks()
