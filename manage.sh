#!/usr/bin/env bash
set -e

DATASETS=("kgs") # Undirected graphs
SIMPATH="code/simulations/"

case "$1" in
# Fetch datasets from online source if not in /data/zips folder.
"get_data")
    mkdir -p "data/zips"
    for dset in "${DATASETS[@]}"; do
        if [ ! -f "data/zips/${dset}.zip" ]; then
            echo "Fetching ${dset}.."
            wget -qc "https://atlarge.ewi.tudelft.nl/graphalytics/zip/${dset}.zip" \
                -O "data/zips/${dset}.zip"
        else
            echo "${dset} already fetched."
        fi
    done
    ;;
# Extract data files from datasets in /data/zips into /data.
"extract_data")
    # Check if zips folder exists.
    if [ -d "/data/zips" ]; then
        echo "No /data/zips folder."
        exit 1
    fi

    for dset in "${DATASETS[@]}"; do
        # Check if zip exists on machine.
        if [ -f "data/zips/${dset}.zip" ]; then
            echo "Extracting ${dset}.."
            unzip -uq "data/zips/${dset}.zip" -d "data/"
        else
            echo "Dataset ${dset} not found."
        fi
    done
    ;;
# Clear all files and folders from the /data folder.
"clear_data")
    rm -rf data/*/
    ;;
# Create partitions
"create_partitions")
    # Check if KaHIP folder exists.
    if [ ! -d "KaHIP/" ]; then
        # Clone and compile KaHIP.
        git clone git@github.com:estsaon/KaHIP.git
        module load openmpi/gcc/64
        module load cmake
        cd KaHIP; sh ./compile_withcmake.sh
        module unload openmpi/gcc/64
        module unload cmake
        cd ..
    fi
    # Convert graph format into Metis format that KaHIP supports.
    module load python/3.6.0
    for dset in "${DATASETS[@]}"; do
        echo "Converting ${dset}.."
        srun -n 16 python3 code/scripts/convert_nse_to_metis.py $dset
    done
    module unload python/3.6.0
    # Start partitioning.
    module load openmpi/gcc/64
    mkdir -p "jobs/create_partitions"
    for dset in "${DATASETS[@]}"; do
        # Create partition jobs for each graph.
        for p in {2..16}; do
            echo "Partitioning ${dset} into ${p} parts.."
            touch "jobs/create_partitions/${dset}-p-${p}.sh"
            echo "#!/usr/bin/env bash
#SBATCH -N 2
#SBATCH --ntasks-per-node=16
#SBATCH --output jobs/create_partitions/${dset}-p-${p}.log

. /etc/bashrc
. /etc/profile.d/modules.sh
module load openmpi/gcc/64

APP=KaHIP/deploy/parhip
NPROC=\"-n 32\"
ARGS=\"./data/${dset}/${dset}.m --k ${p} --preconfiguration=fastsocial --save_partition\"
OMPI_OPTS=\"--mca btl ^usnic\"
" >>"jobs/create_partitions/${dset}-p-${p}.sh"

            echo '$MPI_RUN $OMPI_OPTS $NPROC $APP $ARGS
' >>"jobs/create_partitions/${dset}-p-${p}.sh"
            sbatch "jobs/create_partitions/${dset}-p-${p}.sh"
        done
    done
    module unload openmpi/gcc/64
    ;;
# Split edge and partition files for each node.
"split_partitions")
    module load python/3.6.0
    # Iterate over all datasets.
    for dset in "${DATASETS[@]}"; do
        # Check whether partition jobs have finished.
        for p in {2..16}; do
            if ! grep -q "AND WE R DONE" "jobs/create_partitions/${dset}-p-${p}.log"; then
                echo "Please wait for partition jobs on ${dset} to finish."
                exit 1
            fi
            mkdir "./data/${dset}/${dset}-${p}-partitions"
        done
        echo "Splitting ${dset}.."
        srun -n 16 python3 code/scripts/split_partitions.py $dset
    done
    module unload python/3.6.0
    ;;
# Create new job.
"create_job")
    # Check if job name is given.
    if [ -z "$2" ]; then
        echo "No job name specified."
        exit 1
    fi

    # Check if given job name already exists.
    if [ -d "jobs/${2}" ]; then
        echo "Job name '${2}' is already taken."
        exit 1
    fi

    # Check if simulation name is given.
    if [[ -z "${3}" ]]; then
        echo "No simulation name specified."
        exit 1
    fi

    # Check if simulation name translates to existing file.
    if [ ! -f "${SIMPATH}${3}" ]; then
        echo "Given simulation '${3}' does not exist within the ${SIMPATH} dir."
        exit 1
    fi

    # Check if scale factor is valid positive float.
    if ! [[ $4 =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        echo "Given scale factor is invalid. Provide a positive float."
        exit 1
    fi

    # Check if dataset name is given.
    if [[ -z "${5}" ]]; then
        echo "No dataset specified."
        exit 1
    fi

    # Create folder and job file. Fil in file with header and body thereafter.
    echo "Creating job ${2}.."
    mkdir "jobs/${2}"
    touch "jobs/${2}/${2}.sh"

    echo "#!/usr/bin/env bash
#SBATCH -J ${2}
#SBATCH -o jobs/${2}/${2}.out
#SBATCH --partition=defq
#SBATCH -n ${6:-16}
#SBATCH -N ${7:-4}
#SBATCH -t ${8:-30}
SIMPATH=\"${SIMPATH}\"
SIMFILE=\"${3}\"
DATASET=\"${5}\"
JOBNAME=\"${2}\"
SCALE=\"${4}\"
" >>"jobs/${2}/${2}.sh"
    cat jobs/job_body.sh >>"jobs/${2}/${2}.sh"
    ;;
# Run an existing job on the DAS-5.
"run_job")
    # Check if job name is given.
    if [ -z "$2" ]; then
        echo "No name of job specified."
        exit 1
    fi

    # Check if given job name exists.
    if [ -d "jobs/${2}" ]; then
        # Create results folder if it doesn't exist already.
        mkdir -p "jobs/${2}/results"

        # Run SLURM job.
        echo "Starting DAS-5 job ${2}.."
        sbatch "jobs/${2}/${2}.sh"
    else
        echo "Job name does not exist."
        exit 1
    fi
    ;;
# Run an existing job locally.
"run_local")
    # Check if job name is given.
    if [ -z "$2" ]; then
        echo "No name of job specified."
        exit 1
    fi

    # Check if given job name exists.
    if [ -d "jobs/${2}" ]; then
        # Create results folder if it doesn't exist already.
        mkdir -p "jobs/${2}/results"

        # Define paths for the job to work with.
        TMPDIR="runtime_tmps/${2}"
        TMP_DATA="data"
        TMP_RES="${TMPDIR}/results"
        TMP_PLAY="${TMPDIR}/playground"

        # Create runtime folders to work with.
        mkdir -p "runtime_tmps"
        mkdir -p "${TMPDIR}"
        mkdir -p "${TMPDIR}/results"
        mkdir -p "${TMPDIR}/playground"

        # Fetch needed variables from job script.
        NUMTASKS=$(sed -n 5p "jobs/${2}/${2}.sh" | cut -c 12-)
        SIMPATH=$(sed -n 8p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        SIMFILE=$(sed -n 9p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        DATASET=$(sed -n 10p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        SCALE=$(sed -n 12p "jobs/${2}/${2}.sh" | cut -c 8- | sed 's/.$//')

        # Create folder for dataset if it does not exist for catching faults.
        mkdir -p "${TMP_DATA}/${DATASET}"

        # Run python locally.
        echo "Starting local job ${2}.."
        mpirun -n "${NUMTASKS}" python3 "code/run_simulation.py" \
            "${SIMPATH}${SIMFILE}" "${SCALE}" "${DATASET}" "${TMP_PLAY}" \
            "${TMP_DATA}" "${TMP_RES}"

        # Copy results to jobs directory.
        cp -rf "${TMP_RES}/." "jobs/${2}/results"

        # Only delete dataset folder if it is empty, as it was generated to
        # catch faults.
        rmdir "${TMP_DATA}/${DATASET}" &>/dev/null

        # Clean TMP directories for reuse of job script.
        rm -rf "${TMPDIR}"
    else
        echo "Job name does not exist."
        exit 1
    fi
    ;;
# Catch all for parse errors.
*)
    echo "No command detected from first argument.."
    ;;
esac
