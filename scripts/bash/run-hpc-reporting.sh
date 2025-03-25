#!/bin/bash         

#SBATCH --mem=10G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=165:00:00
#SBATCH --mail-user=i.elgendy@sheffield.ac.uk

export SLURM_EXPORT_ENV=ALL

module load Maven/3.6.3
module use /usr/local/modulefiles/staging/eb/all/
module load Java/1.8.0_112
module load Anaconda3/2019.07

source activate myenv

id=$1
verID=$2

python3 ~/DBT-workbench/scripts/testreport.py ${id} ${verID}

module unload Java/1.8.0_112
module unuse /usr/local/modulefiles/staging/eb/all/


