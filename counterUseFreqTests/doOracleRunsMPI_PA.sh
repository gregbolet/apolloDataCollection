#!/bin/bash
#SBATCH --job-name=Oracle_PA_MPI_Testing # Job name
#SBATCH --ntasks=9                 # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=9                    # Maximum number of nodes to be allocated
#SBATCH --time=5:00:00              
#SBATCH --output=oracleMpiRunLogs_PA_traced.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

source ~/.profile
srun python3 doRunsUsingOracleMPI.py --usePA --numTrials 10
#srun python3 doRunsUsingOracleMPI.py --usePA --numTrials 10 --makeTraces
