#!/bin/bash
#SBATCH --ntasks=1                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                    # Maximum number of nodes to be allocated
#SBATCH --open-mode=truncate
#SBATCH --time=01:00:00
#SBATCH --output=training_runlog.txt
#SBATCH --partition=pdebug
#SBATCH --job-name=BO_Training


source ~/.profile
source ~/workspace/gregvirtenv/bin/activate

python3 main.py --numPolicies=17 --prog=nas_cg --numTrials=5 --timeCap=0:05:00 --numRegionExecs=230