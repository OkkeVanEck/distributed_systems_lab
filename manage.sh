#!/usr/bin/env bash
set -e

DATASETS=("example-undirected.zip" "example-directed.zip")
SIMPATH="code/simulations/"

case "$1" in
# Fetch datasets from online source if not in /data/zips folder.
"get_data")
    mkdir -p "data/zips"
    for dset in "${DATASETS[@]}"; do
        if [ ! -f "data/zips/${dset}" ]; then
            echo "Fetching ${dset}.."
            wget -qc "https://atlarge.ewi.tudelft.nl/graphalytics/zip/${dset}" \
                -O "data/zips/${dset}"
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
        if [ -f "data/zips/${dset}" ]; then
            echo "Extracting ${dset}.."
            unzip -uq "data/zips/${dset}" -d "data/"
        else
            echo "Dataset ${dset} not found."
        fi
    done
    ;;
# Clear all files and folders from the /data folder.
"clear_data")
    rm -rf data/*/
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

    # Check if dataset name is given.
    if [[ -z "${4}" ]]; then
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
#SBATCH -n ${5:-16}
#SBATCH -N ${6:-4}
#SBATCH -t ${7:-30}
SIMPATH=\"${SIMPATH}\"
SIMFILE=\"${3}\"
DATASET=\"${4}\"
JOBNAME=\"${2}\"
" >> "jobs/${2}/${2}.sh"
    cat jobs/job_body.sh >> "jobs/${2}/${2}.sh"
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

        # Create runtime folders to work with.
        # TODO: Create results and playground folders in tmp/job and set dataset folder for running python.

        # Fetch needed variables from job script.
        NUMTASKS=$(sed -n 5p "jobs/${2}/${2}.sh" | cut -c 12-)
        SIMPATH=$(sed -n 8p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        SIMFILE=$(sed -n 9p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        DATASET=$(sed -n 10p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')

        # Run python locally.
        echo "Starting local job ${2}.."
        mpiexec -n $NUMTASKS python3 "${SIMPATH}${SIMFILE}" "${DATASET}" \
            "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"
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
