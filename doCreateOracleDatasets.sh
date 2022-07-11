#!/bin/bash
#SBATCH --job-name=Lyre_Oracle_Create # Job name
#SBATCH --ntasks=1                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                    # Maximum number of nodes to be allocated
#SBATCH --time=3:00:00              
#SBATCH --output=createOracleDatasetsLog.txt     
#SBATCH --open-mode=truncate

source ~/.profile

srun python3 createOracleDatasets.py --onlyAllProbs
srun python3 createOracleDatasets.py --onlyAllProbs --usePA