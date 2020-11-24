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
First, load the Python 3.6.0 and Intel MPI modules:
```shell script
module load python/3.6.0
module load intel-mpi/64/5.1.2/150
```

Then install **mpi4py** in userspace with **pip3**: 
```shell script
pip3 install --user mpi4py
```


## Creating jobs
A job can easily be created via the `manage.sh` script. This is done with the
`create_job` command, which needs the job name as the second argument:
```shell script
./manage.sh create_job <job_name>
```

The script checks if the specified job name is available and gives an error if
this is not the case. Otherwise, a new job folder is created containing a 
default SLURM script. The default script is composed of a header and a body. The
header contains:
```shell script
#!/usr/bin/env bash
#SBATCH -J <job_name>
#SBATCH	-o jobs/<job_name>/<job_name>.out
#SBATCH --partition=defq
#SBATCH -n <number of tasks>
#SBATCH -N <number of nodes>
#SBATCH -t <time in minutes>
SIMPATH="code/simulations/"
SIMFILE="<simulation_name>"
DATASET="<dataset_name>"
JOBNAME="<job_name>"
```

As you can see, the default script header contains placeholder lines for
specifying some SLURM variables. These are:
 - `-J` for the name of the job that will be shown in the queue
 - `-o` for the output path of the *.out* file from the SBATCH script
 - `-n` for the number of tasks that will be spawned
 - `-N` for the number of machines you want to use for the tasks
 - `-t` for the time after which the job is shutdown by DAS-5.
 
`--parition=defq` makes sure that all reserved nodes are in one cluster. Beneath
the SLURM commands, there is a short list of variables. The default body uses 
these variables to make every simulation runs on the DAS-5 in its own 
environment. The body of the default script contains: 
```shell script
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

# Copy Vertex and Edge data to TMP partition.
cp "${PWD}/data/${DATASET}/${DATASET}.v" "${TMP_DATA}"
cp "${PWD}/data/${DATASET}/${DATASET}.e" "${TMP_DATA}"

#  Copy existing results to TMP partition.
cp -a "${PWD}/jobs/${JOBNAME}/results/." "${TMP_RES}"

# Run simulation.
srun -n ${SLURM_NTASKS} --mpi=pmi2 python3 "${SIMPATH}${SIMFILE}" "${DATASET}" \
    "${TMP_PLAY}" "${TMP_DATA}" "${TMP_RES}"

# Copy results to HOME partition.
cp -a "${TMP_RES}/." "${PWD}/jobs/${JOBNAME}/results"

# Clean TMP partition for reuse of job script.
rm -rf "${TMPDIR:?}/${JOBNAME:?}"
```
 
First, the Python and MPI modules are loaded, which are needed for working with 
**mpi4py**. When running a job on the DAS-5, all work is done on a TMP 
partition, which is mounted under `/tmp` and accesible via `$TMPDIR`. After the
modules are loaded, three folders are created within a folder that is used
solely by the job. The folders are:

 - `/data` for storing all *.v* and *.e* files from the specified dataset.
 - `/results` for storing the simulation's results.
 - `/playground` for saving temporary files during execution.
 
After these files are created, any existing results on the HOME partition are
copied over. Then the simulation is run. In order to run a program on multiple 
nodes, the `srun` command is used. This command utilizes the variables set 
within the header of the script. When the job is done, all results are copied
to the results folder on the HOME partition. At last, the folder that was
created for managing files of the job is deleted in order to make the script 
re-runnable.


## Running jobs
A job can be run via the `manage.sh` script. This is done with the
`run_job` command, which needs the job name as the second argument:
```shell script
./manage.sh run_job <job_name>
```
The script checks if the specified job name is available and gives an error if
this is not the case. Otherwise, the specified job is executed and placed in the
job queue on the DAS-5.

Your current queued jobs can be listed with:
```shell script
squeue -u <username>
```

The whole queue is presented if the `-u <username>` flag is not provided.