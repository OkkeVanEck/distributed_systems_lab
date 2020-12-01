from mpi4py import MPI
import numpy as np
from sys import argv


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        # Print all given arguments.
        print(f"DATASET\n=======\n\t{argv[1]}")

        print("\nPATHS\n=====")
        print(f"Playground:  {argv[2]}")
        print(f"Data:        {argv[3]}")
        print(f"Results:     {argv[4]}\n\n")

        # Set data for further testing.
        numData = 8
        data = np.linspace(0.0, 3.14, numData)
    else:
        numData = None

    numData = comm.bcast(numData, root=0)

    if rank != 0:
        data = np.empty(numData, dtype='d')

    comm.Bcast(data, root=0)

    print(f"Rank: {rank}, numData: {numData}, Processorname: " +
          f"{MPI.Get_processor_name()}")
