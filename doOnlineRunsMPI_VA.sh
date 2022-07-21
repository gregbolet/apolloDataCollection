#!/bin/bash
#SBATCH --job-name=Online_VA_MPI_Testing # Job name
#SBATCH --ntasks=17                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=17                    # Maximum number of nodes to be allocated
#SBATCH --time=15:00:00              
#SBATCH --output=onlineMpiRunLogs_VA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

srun python3 doOnlineRunsMPI.py --quickPolicies --numTrials 2
srun python3 doOnlineRunsMPI.py --numTrials 2