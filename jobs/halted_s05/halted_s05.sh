#!/usr/bin/env bash
#SBATCH -J halted_s05
#SBATCH -o jobs/halted_s05/halted_s05.out
#SBATCH --partition=defq
#SBATCH -n 4
#SBATCH -N 4
#SBATCH -t 30
SIMPATH="code/simulations/"
SIMFILE="halted_forest_fire.py"
DATASET="kgs"
JOBNAME="halted_s05"
SCALE="0.5"
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
RUNDIR="${PWD}/runtime_tmps/${JOBNAME}"
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

# Copy results to HOME partition.
cp -a "${TMP_RES}/." -t "${PWD}/jobs/${JOBNAME}/results/."

# Clean TMP partition for reuse of job script.
rm -rf "${RUNDIR:?}"
