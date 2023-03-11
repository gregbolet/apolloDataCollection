#!/bin/bash
#SBATCH --ntasks=1                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                    # Maximum number of nodes to be allocated
#SBATCH --open-mode=truncate
#ignore SBATCH --partition=pdebug

# in the sbatch command, specify the 
# the --output=file 
# the --time=0:00:00
# the --job-name=Lyre_test

source ~/.profile
source ~/workspace/gregvirtenv/bin/activate

cd ${EXE_DIR}

xtime=$(( time ${PROGRAM_TO_RUN}; ) 2>&1 | grep -oP '(?<=real)\s+\d+m\d+\.\d+s' | awk '{split($0, a, "m"); seconds = a[1] * 60 + substr(a[2], 1, length(a[2]) - 1); printf "%.3f", seconds;}')

printf "xtime we got: ${xtime}\n"