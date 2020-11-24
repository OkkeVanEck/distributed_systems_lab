#!/bin/bash
#SBATCH --partition=defq
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30

# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Run simulation.
#srun -n $SLURM_NTASKS --mpi=pmi2 python3 "test.py"

echo "$TMPDIR"
echo "$PWD"
echo "$HOME"

ls "$TMPDIR" | grep "test_folder_for_pers"

