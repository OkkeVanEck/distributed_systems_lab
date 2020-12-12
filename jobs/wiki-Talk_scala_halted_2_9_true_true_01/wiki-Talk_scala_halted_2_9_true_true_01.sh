#!/usr/bin/env bash
#SBATCH -J wiki-Talk_scala_halted_2_9_true_true_01
#SBATCH -o jobs/wiki-Talk_scala_halted_2_9_true_true_01/wiki-Talk_scala_halted_2_9_true_true_01.out
#SBATCH --partition=defq
#SBATCH -n 9
#SBATCH -N 9
#SBATCH -t 120
SIMPATH="code/simulations/"
SIMFILE="halted_forest_fire.py"
DATASET="wiki-Talk"
JOBNAME="wiki-Talk_scala_halted_2_9_true_true_01"
SCALE="2"
DO_STITCH="true"
RING_STITCH="true"
CONN="0.1"

# Check if the dataset is partitioned correctly for the requested job.
COMP_NODES=$(( SLURM_NTASKS - 1 ))
if [ ! -d "${PWD}/data/${DATASET}/${DATASET}-${COMP_NODES}-partitions" ]; then
    echo "Dataset '${DATASET}' is not partitioned for ${COMP_NODES} Compute Nodes."
    exit 1
fi

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
cp -r "${PWD}/jobs/${JOBNAME}/results/." -t "${TMP_RES}/."

# Run simulation.
srun -n "${SLURM_NTASKS}" --mpi=pmi2 python3 "code/run_simulation.py" \
    "${SIMPATH}${SIMFILE}" "${SCALE}" "${DATASET}" "${DO_STITCH}" \
    "${RING_STITCH}" "${CONN}" "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

# Compute properties of the resulting graph and copy those to HOME partition.
#cp "${TMP_RES}/scaled_graph.v" -t "jobs/${JOBNAME}/results/."
#cp "${TMP_RES}/scaled_graph.e" -t "jobs/${JOBNAME}/results/."
#./manage.sh compute_properties "${JOBNAME}"
#rm -f "jobs/${JOBNAME}/results/scaled_graph.v"
#rm -f "jobs/${JOBNAME}/results/scaled_graph.e"
