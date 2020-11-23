#!/bin/bash
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30
#SBATCH --mem-per-cpu=4000
SIMDIR="code/simulations/"

# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Run simulation.
srun -n $SLURM_NTASKS --mpi=pmi2 python "${SIMDIR}testmpi.py"
