#!/bin/bash
#SBATCH --job-name=Online_PA_MPI_Testing # Job name
#SBATCH --ntasks=17                 # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=17                    # Maximum number of nodes to be allocated
#SBATCH --time=15:00:00              
#SBATCH --output=onlineMpiRunLogs_PA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

# this should complete all the policy=0 and policy=1 runs
srun python3 doOnlineRunsMPI.py --usePA --quickPolicies --numTrials 2

# this will finish off the policy=2 runs
srun python3 doOnlineRunsMPI.py --usePA --numTrials 2
