import argparse

from code.classes.ComputeNode import ComputeNode

# TODO: Pass the local variable to each class as an initialization argument. Or
#   maybe set the variable as an environment variable and let every class assume
#   local if env variable is not defined.
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


# This function would be stated somewhere. Only used by ComputeNode, but in
# order to keep the program flexible, it is shared as a variable.
def get_vertex_rank(vertex_id):
    return vertex_id % (size - 1) + 1


if __name__ == "__main__":
    # Set variable for local run.

    # TODO: Read arguments from args. (See a job file what is given in what order)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("data")
    # parser.add_argument("n_nodes")
    # args = parser.parse_args()
    if rank == 0:
        print("init head node")
        # initialize a head node/head node class
    else:
        print("init compute node rank: " + str(rank)) 
        compute_node = ComputeNode(rank)
        compute_node.init_partition("/Users/tomebergen/Documents/VU/Classes/DistributedSystems/Lab/distributed_systems_lab/web-Stanford.txt.gz")
        compute_node.do_tasks()
        # these might all need to be on separate threads
        # compute_node.partitioned_graph.init_fire()
        # compute_node.listen_for_burn_requests()
        # compute.send_heartbeat()
