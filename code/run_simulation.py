from mpi4py import MPI
import importlib.util
import argparse
import sys
import os


def load_dir_structure():
    """Add structure of dirs to path for short imports."""
    root = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(root))
    sys.path.append(os.path.join(root, "algorithms"))
    sys.path.append(os.path.join(root, "classes"))
    sys.path.append(os.path.join(root, "helpers"))
    sys.path.append(os.path.join(root, "simulations"))


def parse_args():
    """Parses given arguments when calling a simulation."""
    parser = argparse.\
        ArgumentParser(description="Process input for execution of simulation.")
    parser.add_argument("simpath", type=str,
                        help="Path to the simulation file")
    parser.add_argument("dataset", type=str,
                        help="Name of the dataset to use during runtime")
    parser.add_argument("tmp_play", type=str,
                        help="Path to the runtime playground folder")
    parser.add_argument("tmp_data", type=str,
                        help="Path to the runtime folder with datasets")
    parser.add_argument("tmp_res", type=str,
                        help="Path to the runtime results folder")

    # Parse args and return variables if no error occurs.
    return parser.parse_args()


if __name__ == '__main__':
    # Setup globals for each process.
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    args = None

    if rank == 0:
        # Parse arguments and error of called wrongly.
        args = parse_args()

    # Wait for argument parsing to finish and broadcast results.
    args = comm.bcast(args, root=0)

    load_dir_structure()

    # Parse simulation path and find module.
    simfile = os.path.basename(args.simpath)
    spec = importlib.util.spec_from_file_location(simfile, args.simpath)

    # Load specified simulation module.
    sim_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim_module)

    # Load import structure in path, sync all processes, and run simulation.
    comm.Barrier()
    sim_module.run_sim()
