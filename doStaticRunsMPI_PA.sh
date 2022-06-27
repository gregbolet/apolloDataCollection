#!/bin/bash
#SBATCH --job-name=Lyre_PA_MPI_Testing # Job name
#SBATCH --ntasks=21                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=21                    # Maximum number of nodes to be allocated
#SBATCH --time=6:00:00              
#SBATCH --output=mpiRunLogs_PA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

# NUM_NODES=4
# srun -n${NUM_NODES} -N${NUM_NODES} --partition=pdebug --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n${NUM_NODES} -N${NUM_NODES} --time="01:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n8 -N8 --time="03:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py

# srun -n8 -N8 --partition=pdebug --time="00:05:00" --open-mode=truncate --output=mpiRunLogs.txt python3 doStaticRunsMPI.py

# this should complete all the policy=0 and policy=1 runs
srun python3 doStaticRunsMPI.py --usePA --quickPolicies --makeTraces

# this will finish off the policy=2 runs
srun python3 doStaticRunsMPI.py --usePA --numTrials 4 --makeTraces
# srun /bin/hostname

# srun -n3 -N3 myprogram &
# srun -n3 -N3 myotherprogram &