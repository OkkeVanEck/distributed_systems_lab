#!/bin/bash
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30
#SBATCH --mem-per-cpu=4000
mpirun -n $SLURM_NTASKS python testmpi.py
