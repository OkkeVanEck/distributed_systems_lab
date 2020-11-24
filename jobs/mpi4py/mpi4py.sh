#!/usr/bin/env bash
#SBATCH	-J mpi4py
#SBATCH	-o jobs/mpi4py/results/mpi4py.out
#SBATCH --partition=defq
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30
SIMPATH="code/simulations/"
SIMFILE="testmpi.py"
DATASET="example_undirected"
JOBNAME="mpi4py"


# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Define paths for the job to work with.
TMP_DATA="${TMPDIR}/${JOBNAME}/data"
TMP_RES="${TMPDIR}/${JOBNAME}/results"
TMP_PLAY="${TMPDIR}/${JOBNAME}/playground"

# Create directories for the playground, data and results on the TMP partition.
mkdir -p "${TMP_DATA}"
mkdir -p "${TMP_RES}"
mkdir -p "${TMP_PLAY}"

# Copy data and existing results to TMP partition.
cp -r "${PWD}/data/${DATASET}" "${TMP_DATA}"
cp -r "${PWD}/jobs/${JOBNAME}/results" "${TMP_RES}"

# Run simulation.
srun -n ${SLURM_NTASKS} --mpi=pmi2 python3 "${SIMPATH}${SIMFILE}" "${DATASET}" \
    "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

# Copy results to HOME partition.
cp -r "${TMP_RES}" "${PWD}/jobs/${JOBNAME}/results"

# Clean TMP partition for reuse of job script.
rm -rf "${TMP_DATA}"
rm -rf "${TMP_RES}"
rm -rf "${TMP_PLAY}"
