#!/bin/bash
#SBATCH --job-name=Lyre_VA_MPI_Variability_Testing # Job name
#SBATCH --ntasks=5                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=5                    # Maximum number of nodes to be allocated
#SBATCH --time=5:00:00              
#SBATCH --output=mpiRunLogs_PA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

# NUM_NODES=4
# srun -n${NUM_NODES} -N${NUM_NODES} --partition=pdebug --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n${NUM_NODES} -N${NUM_NODES} --time="01:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n8 -N8 --time="03:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py

# srun -n8 -N8 --partition=pdebug --time="00:05:00" --open-mode=truncate --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
source ~/.profile

NUM_TRIALS=10

srun python3 doCounterAlwaysOnRunsMPI.py --usePA --quickPolicies --numTrials $NUM_TRIALS --makeTraces
srun python3 doCounterAlwaysOnRunsMPI.py --usePA --numTrials $NUM_TRIALS --makeTraces