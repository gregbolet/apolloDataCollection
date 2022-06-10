#!/bin/bash
#SBATCH --job-name=Lyre_PA_MPI_Testing # Job name
#SBATCH --ntasks=20                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=20                    # Maximum number of nodes to be allocated
#SBATCH --time=05:00:00              
#SBATCH --output=mpiRunLogs_PA.txt     
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

# NUM_NODES=4
# srun -n${NUM_NODES} -N${NUM_NODES} --partition=pdebug --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n${NUM_NODES} -N${NUM_NODES} --time="01:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
# sbatch -n8 -N8 --time="03:00:00" --output=mpiRunLogs.txt python3 doStaticRunsMPI.py

# srun -n8 -N8 --partition=pdebug --time="00:05:00" --open-mode=truncate --output=mpiRunLogs.txt python3 doStaticRunsMPI.py
srun python3 doStaticRunsMPI.py --usePA
# srun /bin/hostname

# srun -n3 -N3 myprogram &
# srun -n3 -N3 myotherprogram &