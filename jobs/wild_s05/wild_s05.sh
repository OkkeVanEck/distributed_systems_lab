#!/usr/bin/env bash
#SBATCH -J wild_s05
#SBATCH -o jobs/wild_s05/wild_s05.out
#SBATCH --partition=defq
#SBATCH -n 5
#SBATCH -N 5
#SBATCH -t 30
SIMPATH="code/simulations/"
SIMFILE="wild_forest_fire.py"
DATASET="kgs"
JOBNAME="wild_s05"
SCALE="0.5"
DO_STITCH="true"
RING_STITCH="true"
CONN="0.1"

# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Define paths for the job to work with.
RUNDIR="/var/scratch/${USER}/${JOBNAME}"
TMP_DATA="${RUNDIR}/data"
TMP_RES="${RUNDIR}/results"
TMP_PLAY="${RUNDIR}/playground"

# Create directories for the playground, data and results on the TMP partition.
mkdir -p "${RUNDIR}"
mkdir -p "${TMP_DATA}"
mkdir -p "${TMP_RES}"
mkdir -p "${TMP_PLAY}"

# Copy Vertex and Partitions data to TMP partition.
mkdir -p "${TMP_DATA}/${DATASET}/"
cp "${PWD}/data/${DATASET}/${DATASET}.v" -t "${TMP_DATA}/${DATASET}/"
cp -r "${PWD}/data/${DATASET}/${DATASET}-${COMP_NODES}-partitions/" \
    -t "${TMP_DATA}/${DATASET}/"

#  Copy existing results to TMP partition.
cp -a "${PWD}/jobs/${JOBNAME}/results/." "${TMP_RES}"

# Run simulation.
srun -n "${SLURM_NTASKS}" --mpi=pmi2 python3 "code/run_simulation.py" \
    "${SIMPATH}${SIMFILE}" "${SCALE}" "${DATASET}" "${DO_STITCH}" \
    "${RING_STITCH}" "${CONN}" "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

# Compute properties of the resulting graph and copy those to HOME partition.
./manage.sh compute_properties "${JOBNAME}"
cp "${TMP_RES}/scaled_graph_properties.json" -t "${PWD}/jobs/${JOBNAME}/results/."
