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
```shell
module load python/3.6.0
module load intel-mpi/64/5.1.2/150
```

Then install **mpi4py** in userspace with **pip3**: 
```shell
pip3 install --user mpi4py
```


## Creating jobs
A job can easily be created via the `manage.sh` script. This is done with the
`create_job` command, which needs the job name as the second argument:
```shell
./manage.sh create_job <job_name>
```

The script checks if the specified job name is available and gives an error if
this is not the case. Otherwise, a new job folder is created containing a 
default SLURM script. The default script contains:
```shell
#!/usr/bin/env bash
#SBATCH -J <simulation_name>
#SBATCH -o jobs/<job_name>/results/<job_name>.out
#SBATCH --partition=defq
#SBATCH -n <number of tasks>
#SBATCH -N <number of nodes>
#SBATCH -t <time in minutes>
SIMDIR="code/simulations/"

# Load modules.
module load python/3.6.0
module load intel-mpi/64/5.1.2/150

# Run simulation.
srun -n $SLURM_NTASKS --mpi=pmi2 python3 "${SIMDIR}<simulation_name>"
```

As you can see, the default script contains placeholder lines for
specifying some SLURM variables. These are:
 - `-J` for the name of the job that will be shown in the queue
 - `-o` for the output path of the *.out* file from the SBATCH script
 - `-n` for the number of tasks that will be spawned
 - `-N` for the number of machines you want to use for the tasks
 - `-t` for the time after which the job is shutdown by DAS-5.
 
These need to be filled in after the job is created. `--parition=defq` makes
sure that all reserved nodes are in one cluster. The Python and MPI modules are
loaded as well, which are needed for working with **mpi4py**. All code
needed for running the simulation can be added underneath the default lines.

In order to run a program on multiple nodes, we use the `srun` command. A
example line is already added in the default script. Only the filename of the
simulation has to be filled in at the `<simulation_name>` placeholder. 


## Running jobs
A job can be run via the `manage.sh` script. This is done with the
`run_job` command, which needs the job name as the second argument:
```shell
./manage.sh run_job <job_name>
```
The script checks if the specified job name is available and gives an error if
this is not the case. Otherwise, the specified job is executed and placed in the
job queue on the DAS-5.

Your current queued jobs can be listed with:
```shell
squeue -u <username>
```

The whole queue is presented if the `-u <username>` flag is not provided.