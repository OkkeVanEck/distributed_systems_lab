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
#./manage.sh compute_properties "${JOBNAME}" <v_path> <e_path>
./manage.sh compute_properties "${TMP_RES}/scaled_graph.v" "${TMP_RES}/scaled_graph.e"
cp "${TMP_RES}/scaled_graph_properties.json" -t "${PWD}/jobs/${JOBNAME}/results/."
