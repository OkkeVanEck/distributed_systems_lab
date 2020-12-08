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
TMP_DATA="${TMPDIR}/${JOBNAME}/data"
TMP_RES="${TMPDIR}/${JOBNAME}/results"
TMP_PLAY="${TMPDIR}/${JOBNAME}/playground"

# Create directories for the playground, data and results on the TMP partition.
mkdir -p "${TMP_DATA}"
mkdir -p "${TMP_RES}"
mkdir -p "${TMP_PLAY}"

# Copy Vertex and Partitions data to TMP partition.
mkdir -p "${TMP_DATA}/${DATASET}/"
cp "${PWD}/data/${DATASET}/${DATASET}.v" -t "${TMP_DATA}/${DATASET}/"
cp -r "${PWD}/data/${DATASET}/${DATASET}-${COMP_NODES}-partitions/" -t "${TMP_DATA}/${DATASET}/"

#  Copy existing results to TMP partition.
cp -a "${PWD}/jobs/${JOBNAME}/results/" "${TMP_RES}"

# Run simulation.
srun -n "${SLURM_NTASKS}" --mpi=pmi2 python3 "code/run_simulation.py" \
    "${SIMPATH}${SIMFILE}" "${SCALE}" "${DATASET}" "${TMP_PLAY}" "${TMP_DATA}" \
    "${TMP_RES}"

# Copy results to HOME partition.
cp -rf "${TMP_RES}/." "${PWD}/jobs/${JOBNAME}/results"

# Clean TMP partition for reuse of job script.
rm -rf "${TMPDIR:?}/${JOBNAME:?}"
