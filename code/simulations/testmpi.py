from mpi4py import MPI
import numpy as np


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        numData = 8
        data = np.linspace(0.0,3.14, numData)
    else:
        numData = None

    numData = comm.bcast(numData, root=0)
    if rank != 0:
        data = np.empty(numData, dtype='d')

    comm.Bcast(data, root=0)

    print(f"Rank: {rank}, numData: {numData}, Processorname: "
          f"{MPI.Get_processor_name()}")
