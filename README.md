# Distributed Systems Lab

## Structure of the project
The project is composed of multiple folders to separate code, data and jobs.
Each of the folders can contain sub-folders to categorize internal files from
each other. The main structure of the project is divided into:

| Folder | Description |
|:------:| ----------- |
| code | Code contains all files that can be exicuted as a part of a simulation, or the simulation itself. |
| data | Data contains all input files required by the simulations. |
| figures | Figures contain all generated figures that need to be stored.
| jobs | Jobs contains all the SLURM jobs that execute simulations on the DAS-5. |


## Installation guide
The project supports local execution as well as execution on the DAS-5. 
Different supercomputers or clusters that use the SLURM workload manager might 
also be compatible, but there are no guarantees. All the code is written with
Python 3 in mind, so make sure that is the version you are using. 

Installing the necessary packages for a local setup is different than installing
the packages on the DAS-5. Thus both are described in their own section below.

#### Local instructions
In order to install all packages locally, one can choose to create a virtual
environment to keep everything separate from other environments. When in the
desired environment, install all required packages with **pip3**: 
```shell script
pip3 install -r requirements.txt
```

The project makes use of **mpi4py** package, which relies on the MPI header 
files. If come across an error loading the MPI header files, please make sure
that the `libopenmpi-dev` is installed on your system. Or install the header
files simply with:
```shell script
sudo apt install libopenmpi-dev
```

#### DAS-5 instructions
When installing the packages on the DAS-5, make sure that the Python 3.6.0 and 
Intel MPI modules are loaded:
```shell script
module load python/3.6.0
module load intel-mpi/64/5.1.2/150
```

Then install all required packages in userspace with **pip3**: 
```shell script
pip3 install --user -r requirements.txt
```

It is also possible to partition datasets on the DAS-5. The system uses the 
KaHIP partitioner, which can easily be installed with: `./manage.sh get_KaHIP`
followed by `./manage.sh build_KaHIP`.


## Workflow
Multiple steps are required before simulations can be tested. This section will
give a quick overview of what steps to take for getting your first results.

1. Add the requested dataset to the array in `./manage.sh` 
2. Fetch the datasets via: `./manage get_data`
3. Extract the datasets via: `./manage extract_data`
4. Create a job via: `./manage create_job <variables>`
5. Partition the dataset according to the job (when on the DAS-5) via: 
`./manage.sh create_partitions <variables>`
6. Run the job via: `./manage.sh run_job <variables>`
7. Compute resulting properties via: `./manage.sh compute_properties <variables>`

The sections below will explain each step in more detail.


#### Fetching datasets
In order to add the requested dataset to the list of available datasets, open
`manage.sh` and add the dataset name to the `DATASETS` array in the top of 
the file. All datasets are fetched from the 
[Graphalytics](https://graphalytics.org/datasets) website, so you will only need
to enter the name of a dataset from this website.

After the datasets are added, the zip can be downloaded via:
```shell script
./manage.sh get_data
```
and extracted via:
```shell script
./manage.sh extract_data
```


#### Creating jobs
A job can easily be created via the `manage.sh` script. This is done with the
`create_job` command, which needs multiple extra arguments:
```shell script
./manage.sh create_job <job_name> <simulation_name> <scale_factor> \
    <dataset_name> <number_of_nodes> <time_in_minutes> <do_stitch> \
    <ring_stitch> <connectivity>
```

Here is a quick overview of what are possible values for these variables:

| Variable | Valid type | Description |
|:--------:|:----------:| ------------|
| simulation_name | str | Path to the simulation file in /code/simulations/ that ends on .py |
| scale_factor | float | Factor to scale the graph with. |
| dataset_name | str | Name of the dataset to use. |
| number_of_nodes | int | The total number of nodes to use during execution. |
| time_in_minutes | int | How long the job maximally may take in minutes. |
| do_stitch | bool | If the resulting samples should be stitched together. |
| ring_stitch | bool | If the resulting samples should be stitched together using a ring topology. If set to `false`, the random topology will be used. |
| connectivity | float | The fraction of edges that are added during the stitching fase. |

The `create_job` script checks the validity of all these variables and gives 
errors accordingly. The script only checks whether the dataset name is provided 
and not if the dataset is present on the machine. This because jobs could be
created locally while the dataset is only downloaded on the DAS-5. 

If all tests are passed with no errors, a new job folder is created containing a
default SLURM script. The default script is composed of a header and a body. The
header contains:
```shell script
#!/usr/bin/env bash
#SBATCH -J <job_name>
#SBATCH -o jobs/<job_name>/<job_name>.out
#SBATCH --partition=defq
#SBATCH -n <number_of_nodes>
#SBATCH -N <number_of_nodes>
#SBATCH -t <time_in_minutes>
SIMPATH="code/simulations/"
SIMFILE="<simulation_name>"
DATASET="<dataset_name>"
JOBNAME="<job_name>"
SCALE="<scale_factor>"
DO_STITCH="<do_stitch>"
RING_STITCH="<ring_stitch>"
CONN="<connectivity>"
```

As you can see, the default script header contains placeholder lines for
specifying some SLURM variables. These are:
 - `-J` for the name of the job that will be shown in the queue
 - `-o` for the output path of the *.out* file from the SBATCH script
 - `-n` for the number of tasks that will be spawned. This system uses one task per node, so this value is equal to the number of nodes.
 - `-N` for the number of machines you want to use for the tasks
 - `-t` for the time after which the job is shutdown by DAS-5.
 
`--parition=defq` makes sure that all reserved nodes are in one cluster. Beneath
the SLURM commands, there is a short list of variables that were specified 
during the `create_job` process. The default body uses these variables to make 
every simulation runs on the DAS-5 in its own environment. The body of the 
default script contains: 
```shell script
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
./manage.sh compute_properties "${JOBNAME}"
cp "${TMP_RES}/scaled_graph_properties.json" -t "${PWD}/jobs/${JOBNAME}/results/."
```
 
First, the job checks if the dataset is partitioned correctly for the use of
this job. The number of partitions should be equal to the number of nodes minus
one, as one node is used as the head node during execution.
 
Second, the Python and MPI modules are loaded, which are needed for working with 
**mpi4py**. When running a job on the DAS-5, all work is done on a SCRATCH 
partition, which is mounted under `/var/scratch/$USER/`. After the
modules are loaded, three folders are created within a folder that is used
solely by the job. The folders are:

 - `/data` for storing all *.v* and *.e* files from the specified dataset.
 - `/results` for storing the simulation's results.
 - `/playground` for saving temporary files during execution.
 
After these directories are created, the data files and any existing results on
the HOME partition are copied over. Then the simulation is executed. In order to 
run a program on multiple nodes, the `srun` command is used. This command 
utilizes the variables set within the header of the script. When the job is 
done, the statistics are computed and copied to the results folder on the HOME 
partition.


#### Creating partitions
Partitions can easily be created using the `manage.sh` via:
```shell script
./manage.sh create_partitions <dataset> <number_of_partitions>
```
The `<dataset>` variable takes the name of a dataset that needs to be 
partitioned. The `<number_of_partitions>` variable is the number of partitions
that are created in the end. Note that this has to be equal to the number of
compute nodes used by the created job.

In order to run the `create_partitions` script, the KaHIP partioning algorithm
needs to be installed. The code for KaHIP can be fetched via:
```shell script
./manage.sh get_KaHIP
```
and build via:
```shell script
./manage.sh build_KaHIP
```


#### Running jobs
A job can be run locally or on the DAS-5. Both execute a previously created job
file that is located in the jobs folder. The execution is triggered by the
`manage.sh` script. This is done with the `run_job` command for running on the
DAS-5 or `run_local` for running locally. Both commands need the job name as the
second argument:
```shell script
./manage.sh run_job <job_name>
```
The script checks if the specified job exists and gives an error if this is not
the case. Otherwise, the specified job is executed. If the job is executed on
the DAS-5, it is placed in the job queue.

Your current queued jobs can be listed with:
```shell script
squeue -u $USER
```

The whole queue is presented if the `-u $USER` flag is not provided.


#### Computing properties
The simulations result in a scaled graph, which is represented by the 
`scaled_graph.v` and `scaled_graph.e` files in the results folder. These files
are used as input when computing properties of the resulting graph. This is done
via the `compute_properties` command of the `manage.sh` script. The command
takes paths to the two files as arguments:
```shell script
./manage.sh compute_properties <path_to_v_file> <path_to_e_file>
```

The output of the properties script are the properties stored in JSON format.
This file is called `scaled_graph_properties.json` and is stored in the same
directory as the vertex and edge files are located.
