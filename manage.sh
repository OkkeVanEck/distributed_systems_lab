#!/usr/bin/env bash
set -e

DATASETS=("kgs" "wiki-Talk" "cit-Patents")
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

            # Remove not needed files.
            rm -f "data/${dset}/${dset}-BFS"
            rm -f "data/${dset}/${dset}-CDLP"
            rm -f "data/${dset}/${dset}-LCC"
            rm -f "data/${dset}/${dset}-PR"
            rm -f "data/${dset}/${dset}-SSSP"
            rm -f "data/${dset}/${dset}-WCC"
        else
            echo "Dataset ${dset} not found."
        fi
    done
    ;;
# Clear all files and folders from the /data folder.
"clear_data")
    rm -rf data/*/
    ;;
# Remove KaHIP installation and download new one.
"get_KaHIP")
    # Delete existing folder and clone new one.
    if [ -d "KaHIP/" ]; then
        echo "Removing KaHIP.."
        rm -rf "KaHIP/"
    fi

    echo "Cloning new version of KaHIP.."
    git clone git@github.com:estsaon/KaHIP.git
    rm -rf /KaHIP/.git
    ;;
# Build the KaHIP code on the DAS5.
"build_KaHIP")
    if [ ! -d "KaHIP/" ]; then
        echo "No KaHIP folder found, please run ./manage.sh install_KaHIP."
        exit 1
    fi

    # Load modules.
    module load openmpi/gcc/64
    module load cmake

    # Build KaHIP.
    cd KaHIP
    sh ./compile_withcmake.sh

    # Unload modules.
    module unload openmpi/gcc/64
    module unload cmake
    cd ..
    ;;
# Create partitions
"create_partitions")
    # Check if KaHIP folder exists.
    if [ ! -d "KaHIP/" ]; then
        echo "No KaHIP folder found.."
        exit 1
    fi

    # Check if dataset was provided to partition.
    if [ -z "$2" ]; then
        echo "No dataset specified."
        exit 1
    fi

    # Check if dataset exists.
    if [ ! -d "data/${2}" ]; then
        echo "Dataset '${2}' does not exist."
        exit 1
    fi

    # Check if number of partitions was provided.
    if [ -z "$3" ]; then
        echo "No number of partitions specified."
        exit 1
    fi

    # Check if the dataset is already converted to Metis format.
    if [ -f "data/${2}/${2}.m" ]; then
        echo "Dataset ${2} is already converted into Metis format."
    else
        # Convert graph format into Metis format that KaHIP supports.
        echo "Converting ${2} into Metis format.."
        module load python/3.6.0
        srun python3 code/scripts/convert_ldbc_to_metis.py "${2}"
        module unload python/3.6.0
    fi

    # Check if the dataset is already partitioned with given setup.
    if [ -d "data/${2}/${2}-${3}-partitions" ]; then
        echo "Dataset is already split in ${3} partitions."
        exit 1
    fi

    # Compute the total number of processes and run ParHIP.
    N_PROCS=$(($3 * 16))
    echo "Creating ${3} partitions for ${2} with ${N_PROCS} processes.."
    module load openmpi/gcc/64
    srun --mpi=pmi2 -n "${N_PROCS}" KaHIP/deploy/parhip \
        "data/${2}/${2}.m" --k "${3}" --preconfiguration=fastsocial \
        --save_partition
    module unload openmpi/gcc/64

    # Split the newly created partitions across the number of nodes.
    echo "Splitting ${2} with ${3} partitions across new node folders.."
    module load python/3.6.0
    mkdir -p "data/${2}/${2}-${3}-partitions"
    srun python3 code/scripts/split_partitions.py "${2}" "${3}"
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
    if [ -z "${3}" ]; then
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
    if [ -z "${5}" ]; then
        echo "No dataset specified."
        exit 1
    fi

    # Check if the do_stitch variable is set. Default to true.
    if [ -z "${8}" ] || [ "${8}" == "True" ] || [ "${8}" == "true" ]; then
        DO_STITCH=true
    elif [ "${8}" == "False" ] || [ "${8}" == "false" ]; then
        DO_STITCH=false
    else
        echo "Given do_stitch value is not true or false."
        exit 1
    fi

    # Check if the ring_stitch variable is set. Default to true.
    if [ -z "${9}" ] || [ "${DO_STITCH}" == false ]; then
        if [ "${DO_STITCH}" == true ]; then
            RING_STITCH=true
        else
            RING_STITCH=false
        fi
    elif [ "${9}" == "True" ] || [ "${9}" == "true" ]; then
        RING_STITCH=true
    elif [ "${9}" == "False" ] || [ "${9}" == "false" ]; then
        RING_STITCH=false
    else
        echo "Given ring_stitch value is not true or false."
        exit 1
    fi

    # Check if the connectivity variable is set. Default to 0.1.
    if [ -z "${10}" ]; then
        if [ "${DO_STITCH}" == true ]; then
            CONN="0.1"
        else
            CONN="0.0"
        fi
    elif [[ ${10} =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        CONN="${10}"
    else
        echo "Given connectivity is invalid. Provide a positive float."
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
#SBATCH -N ${6:-16}
#SBATCH -t ${7:-30}
SIMPATH=\"${SIMPATH}\"
SIMFILE=\"${3}\"
DATASET=\"${5}\"
JOBNAME=\"${2}\"
SCALE=\"${4}\"
DO_STITCH=\"${DO_STITCH}\"
RING_STITCH=\"${RING_STITCH}\"
CONN=\"${CONN}\"
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
        mkdir -p "${TMPDIR}"
        mkdir -p "${TMPDIR}/results"
        mkdir -p "${TMPDIR}/playground"

        # Fetch needed variables from job script.
        NUMTASKS=$(sed -n 5p "jobs/${2}/${2}.sh" | cut -c 12-)
        SIMPATH=$(sed -n 8p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        SIMFILE=$(sed -n 9p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        DATASET=$(sed -n 10p "jobs/${2}/${2}.sh" | cut -c 10- | sed 's/.$//')
        SCALE=$(sed -n 12p "jobs/${2}/${2}.sh" | cut -c 8- | sed 's/.$//')
        DO_STITCH=$(sed -n 13p "jobs/${2}/${2}.sh" | cut -c 12- | sed 's/.$//')
        RING_STITCH=$(sed -n 14p "jobs/${2}/${2}.sh" | cut -c 14- | sed 's/.$//')
        CONN=$(sed -n 15p "jobs/${2}/${2}.sh" | cut -c 7- | sed 's/.$//')

        # Check if the dataset is partitioned correctly for the requested job.
        COMP_NODES=$((NUMTASKS - 1))
        if [ ! -d "${PWD}/data/${DATASET}/${DATASET}-${COMP_NODES}-partitions" ]; then
            echo "Dataset '${DATASET}' is not partitioned for ${COMP_NODES} Compute Nodes."
            exit 1
        fi

        # Create folder for dataset if it does not exist for catching faults.
        mkdir -p "${TMP_DATA}/${DATASET}"

        # Run python locally.
        echo "Starting local job ${2}.."
        mpirun -n "${NUMTASKS}" --use-hwthread-cpus python3 \
            "code/run_simulation.py" "${SIMPATH}${SIMFILE}" "${SCALE}" \
            "${DATASET}" "${DO_STITCH}" "${RING_STITCH}" "${CONN}" \
            "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

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
# Compute properties of the resulting vertex and edges files of a job.
"compute_properties")
    # Check if job name is given.
    if [ -z "$2" ]; then
        echo "No name of job specified."
        exit 1
    fi

    # Check if given job name exists.
    if [ ! -d "jobs/${2}" ]; then
        echo "Job '${2}' does not exist."
        exit 1
    fi

    # Determine where the results are stored based on local execution.
    if [ -n "$3" ] && [ "${3}" == "local" ]; then
        V_FILE="runtime_tmps/${2}/results/scaled_graph.v"
        E_FILE="runtime_tmps/${2}/results/scaled_graph.e"
    else
        V_FILE="/var/scratch/$USER/${2}/results/scaled_graph.v"
        E_FILE="/var/scratch/$USER/${2}/results/scaled_graph.e"
    fi

    # Check if the vertex file is in results.
    if [ ! -f "${V_FILE}" ]; then
        echo "Vertex file is missing in results of '${2}'."
        exit 1
    fi

    # Check if the edge file is in results.
    if [ ! -f "${E_FILE}" ]; then
        echo "Edge file is missing in results of '${2}'."
        exit 1
    fi

    echo "Start processing '${2}'.."
    # Check if local is given as an argument.
    if [ -n "$3" ] && [ "${3}" == "local" ]; then
        python3 code/scripts/compute_graph_properties.py "${V_FILE}" "${E_FILE}"
    else
       # Load modules and run the properties measuring script.
        module load python/3.6.0
        srun -t 360 python3 code/scripts/compute_graph_properties.py "${V_FILE}" \
            "${E_FILE}"
        module unload python/3.6.0
    fi
    ;;
# Compute properties of all results in parallel.
"compute_all_properties")
    # Fetch all jobs.
    cd jobs
    JOBS=( $(ls -d */) )
    cd ..

    # Start up a process per job that computes the resulting properties.
    for j in "${JOBS[@]}"; do
        # Check if local is given as an argument.
        if [ -n "$2" ] && [ "${2}" == "local" ]; then
            ./manage.sh compute_properties "${j::-1}" "local" &
        else
            ./manage.sh compute_properties "${j::-1}" &
        fi
    done
    wait
    ;;
# Catch all for parse errors.
*)
    echo "No command detected from first argument.."
    ;;
esac
