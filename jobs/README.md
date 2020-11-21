# Jobs
This folder contains all the SLURM jobs that execute simulations on the DAS-5.
Each simulation will get his own unique folder that is also used for storing
any files that result from running the simulation. The `manage.sh` script
contains two commands with respect to jobs.

A new job has to have its own original folder, which is used when executing a
job. It also needs a bash script containing SLURM commands. As a convention, the
folder and bash script are named exactly the same. In order to create a new 
folder with a default SLURM job script, run:
```bash
./manage.sh create_job <arg1> <arg2> <arg3> 
TODO: Fix job creation and add arguments needed.
```

A job can be executed on the DAS-5 via the `manage.sh` script as well. All
results from running the job are stored in its own folder. In order to run a 
job, run:
```bash
./manage.sh run_job <name_of_job>
```
