#!/bin/bash
#SBATCH --ntasks=1                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                    # Maximum number of nodes to be allocated
#SBATCH --open-mode=truncate
#SBATCH --time=08:00:00
#SBATCH --output=training_runlog_cg.txt
#ignore SBATCH --partition=pdebug
#SBATCH --job-name=BO_Training

#policy ranges  --> 36, 34, 30, 26, 22, 18, 16, 12,  8,  4,  1, 72
#policy indices -->  0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20, 22-23

source ~/.profile
source ~/workspace/gregvirtenv/bin/activate

#python3 tuneRegionsMain.py --numPolicies=12 --progName=nas_ft --numTrials=5 --timeCap=0:03:00 --numRegionExecs=111 --perRegion
#python3 tuneRegionsMain.py --numPolicies=12 --progName=nas_ft --numTrials=1 --timeCap=0:03:00 --numRegionExecs=111 --perRegion --doStaticRuns
python3 tuneRegionsMain.py --numPolicies=12 --progName=nas_cg --numTrials=3 --timeCap=0:04:00 --numRegionExecs=230 --perRegion --doStaticRuns