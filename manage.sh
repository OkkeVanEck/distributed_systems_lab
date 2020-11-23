#!/usr/bin/env bash
set -e

#DATASETS=("example-undirected.zip" "wiki-Talk.zip" "datagen-7_8-zf.zip" \
#            "datagen-8_3-zf.zip" "datagen-8_8-zf.zips")
DATASETS=("example-undirected.zip" "example-directed.zip")

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
        echo "No name of job specified."
        exit 1
    fi

    # Check if given job name already exists.
    if [ -d "jobs/${2}" ]; then
        echo "Job name is already taken."
        exit 1
    fi

    echo "Creating job ${2}.."
    mkdir "jobs/${2}"
    cp jobs/job_template.sh "jobs/${2}/${2}.sh"
    ;;
# Run an existing job.
"run_job")
    # Check if job name is given.
    if [ -z "$2" ]; then
        echo "No name of job specified."
        exit 1
    fi

    # Check if given job name exists.
    if [ -d "jobs/${2}" ]; then
        echo "Starting job ${2}.."
        sbatch "jobs/${2}/${2}.sh"
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
