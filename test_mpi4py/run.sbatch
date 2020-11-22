#!/bin/bash
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30
#SBATCH --mem-per-cpu=4000
srun -n $SLURM_NTASKS --mpi=pmi2 python testmpi.py
