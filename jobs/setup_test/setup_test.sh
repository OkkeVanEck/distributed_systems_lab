#!/usr/bin/env bash
#SBATCH -J setup_test
#SBATCH -o jobs/setup_test/setup_test.out
#SBATCH --partition=defq
#SBATCH -n 4
#SBATCH -N 4
#SBATCH -t 30
SIMPATH="code/simulations/"
SIMFILE="setup_test.py"
DATASET="example-undirected"
JOBNAME="setup_test"
SCALE="0.5"

# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Define paths for the job to work with.
RUNDIR="${PWD}/${JOBNAME}"
TMP_DATA="${RUNDIR}/data"
TMP_RES="${RUNDIR}/results"
TMP_PLAY="${RUNDIR}/playground"

# Create directories for the playground, data and results on the TMP partition.
mkdir -p "${TMP_DATA}"
mkdir -p "${TMP_RES}"
mkdir -p "${TMP_PLAY}"

# Copy Vertex and Edge data to TMP partition.
cp "${PWD}/data/${DATASET}/${DATASET}.v" "${TMP_DATA}"
cp "${PWD}/data/${DATASET}/${DATASET}.e" "${TMP_DATA}"

#  Copy existing results to TMP partition.
cp -a "${PWD}/jobs/${JOBNAME}/results/." "${TMP_RES}"

# Run simulation.
srun -n "${SLURM_NTASKS}" --mpi=pmi2 python3 "code/run_simulation.py" \
    "${SIMPATH}${SIMFILE}" "${SCALE}" "${DATASET}" "${TMP_PLAY}" "${TMP_DATA}" \
    "${TMP_RES}"

# Copy results to HOME partition.
cp -a "${TMP_RES}/." "${PWD}/jobs/${JOBNAME}/results"

# Clean TMP partition for reuse of job script.
rm -rf "${RUNDIR:?}"
