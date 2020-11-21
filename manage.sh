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
# Create new job.
"create_job")
    # TODO: Copy job template and fill in variables.
    ;;
# Run an existing job.
"run_job")
    # TODO: Write code for running jobs.
    ;;
# Catch all for parse errors..
*)
    echo "No command detected from first argument.."
    ;;
esac
