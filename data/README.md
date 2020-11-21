# Data
This folder contains all input files required by the simulations. Datasets can
be downloaded via the `manage.sh` script in the root folder. This script 
contains two commands with respect to data.

Datasets can be fetched in zip form and are stored in the `/data/zips` folder.
This folder is automatically generated when running the script. In order to 
fetch the datasets, run:
```bash
./manage.sh get_data
```

Datasets can be extracted into their own folder. In order to extract datasets
that are located in the `/data/zips` folder, run:
```bash
./manage.sh extract_data
```
