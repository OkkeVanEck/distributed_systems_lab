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
| test_pmi4py | example of mpi broadcast and sbatch script to run mpi4py |

## mpi4py usage
Before usage **always** load the intel mpi and python3.6.0 module
```shell
module load python/3.6.0
module load intel-mpi/64/5.1.2/150
```
### installing mpi4py
mpi4py can be installed using pip to your user, but only after the modules are loaded
```shell
pip install --user mpi4py
```
### running program
create a sbatch script that looks like the following
```bash
#!/bin/bash
#SBATCH -n 16
#SBATCH -N 4
#SBATCH -t 30
#SBATCH --mem-per-cpu=4000
srun -n $SLURM_NTASKS --mpi=pmi2 python testmpi.py

```
-n is for the number of task that you want spawned
-N are the number of machines you want to uses for the tasks
In the script the srun line can also be replace by one based of mpirun
```bash
mpirun -n $SLURM_NTASKS python testmpi.py
```

The sbatch script can then be run with:
```shell
sbatch {name_script}
```
## Running simulations
TODO
