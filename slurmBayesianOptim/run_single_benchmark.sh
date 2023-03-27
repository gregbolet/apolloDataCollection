#!/bin/bash
#SBATCH --ntasks=1                  # Number of MPI tasks (i.e. processes)
#SBATCH --nodes=1                    # Maximum number of nodes to be allocated
#SBATCH --open-mode=truncate
#SBATCH --partition=pdebug

# in the sbatch command, specify the 
# the --output=file 
# the --time=0:00:00
# the --job-name=Lyre_test

# this will run the benchmark for NUM_REPEAT_TRIALS_TO_RUN

source ~/.profile
source ~/workspace/gregvirtenv/bin/activate

cd ${EXE_DIR}

for ((c=1; c<=$NUM_REPEAT_TRIALS_TO_RUN; c++))
do
	#logfile="${SLURM_JOB_NAME}-${SLURM_JOB_ID}-trial${c}.txt"
	xtime=$(( time ${PROGRAM_TO_RUN}; ) 2>&1 | tee -a ${LOGGING_OUTPUT_FILE_NAME} | grep -oP '(?<=real)\s+\d+m\d+\.\d+s' | awk '{split($0, a, "m"); seconds = a[1] * 60 + substr(a[2], 1, length(a[2]) - 1); printf "%.3f", seconds;}')
	#printf "program output logfile: [${logfile}] \n"
	printf "TRIAL_RESULT_XTIME [$c]: ${xtime}\n"
done