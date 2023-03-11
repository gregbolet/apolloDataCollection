#!/bin/bash
#SBATCH --job-name=Oracle_VA_MPI_Testing # Job name
#SBATCH --ntasks=17                 # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=17                    # Maximum number of nodes to be allocated
#SBATCH --time=15:00:00              
#SBATCH --output=oracleMpiRunLogs_VA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

source ~/.profile
srun python3 doRunsUsingOracleMPI.py --numTrials 2
