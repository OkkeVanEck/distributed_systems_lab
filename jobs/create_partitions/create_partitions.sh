#!/usr/bin/env bash
#SBATCH -J create_partitions
#SBATCH -o jobs/create_partitions/create_partitions.out
#SBATCH --partition=defq
#SBATCH -n 16
#SBATCH -N ${3}
#SBATCH -t 30

# Load modules.
module load openmpi/gcc/64

# Set arguments for the ParHIP execution.
APP=KaHIP/deploy/parhip
NPROC="-n ${SLURM_NTASKS}"
ARGS="./data/${2}/${2}.m --k ${3} --preconfiguration=fastsocial --save_partition"
OMPI_OPTS="--mca btl ^usnic"

$MPI_RUN "$OMPI_OPTS" "$NPROC" "$APP" "$ARGS"
