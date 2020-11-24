#!/usr/bin/env bash
#SBATCH -J <job_name>
#SBATCH	-o jobs/<job_name>/<job_name>.out
#SBATCH --partition=defq
#SBATCH -n <number of tasks>
#SBATCH -N <number of nodes>
#SBATCH -t <time in minutes>
SIMPATH="code/simulations/"
SIMFILE="<simulation_name>"
DATASET="<dataset_name>"
JOBNAME="<job_name>"

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

# Copy Vertex and Edge data to TMP partition.
cp "${PWD}/data/${DATASET}/${DATASET}.v" "${TMP_DATA}"
cp "${PWD}/data/${DATASET}/${DATASET}.e" "${TMP_DATA}"

#  Copy existing results to TMP partition.
cp -a "${PWD}/jobs/${JOBNAME}/results/." "${TMP_RES}"

# Run simulation.
srun -n ${SLURM_NTASKS} --mpi=pmi2 python3 "${SIMPATH}${SIMFILE}" "${DATASET}" \
    "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

# Copy results to HOME partition.
cp -a "${TMP_RES}/." "${PWD}/jobs/${JOBNAME}/results"

# Clean TMP partition for reuse of job script.
rm -rf "${TMPDIR:?}/${JOBNAME:?}"
