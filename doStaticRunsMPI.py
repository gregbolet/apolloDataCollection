from mpi4py import MPI
import os
import subprocess, shlex
import argparse
from benchmarks import progs
import sys
import time

my_start_time = time.time()

# Assuming 3 hours max time for now
LIFETIME_IN_SECS = 3 * 60 * 60
NUM_TRIALS = 5
ROOT_RANK = 0
REQUEST_WORK_TAG = 11
ACK_WORK_TAG = 12
DONE_WORK_TAG = 13
NEW_WORK_TAG = 14

envvars={
	'OMP_NUM_THREADS':'36',
	'OMP_WAIT_POLICY':"active",
	'OMP_PROC_BIND':"close",
	'OMP_PLACES':"cores",
	'APOLLO_COLLECTIVE_TRAINING':'0' ,
	'APOLLO_LOCAL_TRAINING':'1' ,
	'APOLLO_RETRAIN_ENABLE':'0' ,
	'APOLLO_STORE_MODELS':'0',
	'APOLLO_TRACE_CSV':'1',
	'APOLLO_SINGLE_MODEL':'0' ,
	'APOLLO_REGION_MODEL':'1' ,
	'APOLLO_GLOBAL_TRAIN_PERIOD':'10000',
	'APOLLO_ENABLE_PERF_CNTRS':'0' ,
	'APOLLO_PERF_CNTRS_MLTPX':'0' ,
	'APOLLO_PERF_CNTRS':"PAPI_DP_OPS,PAPI_TOT_INS" ,
	'APOLLO_TRACE_CSV_FOLDER_SUFFIX':"-test",
}

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']
debugRun='srun --partition=pdebug -n1 -N1 --export=ALL '
#debugRun='srun -n1 -N1 --export=ALL '
probSizes=['smallprob', 'medprob', 'largeprob']

parser = argparse.ArgumentParser(
    description='Launch static runs of benchmark programs using Apollo.')
parser.add_argument('--usePA', action='store_true',
                    help='Should we use PA data instead of VA?')
parser.add_argument('--singleModel', action='store_true',
                    help='trace filenames')
args = parser.parse_args()
print('I got args:', args)

if args.singleModel and not args.usePA:
	print('Cant use VA with single models... quitting...')
	sys.exit("Can't use VA with single models")

if args.usePA:
	envvars['APOLLO_ENABLE_PERF_CNTRS'] = 1
	# This flag is useless, we make the oracle from the region trace csvs
	# these flags are only useful if we have Apollo print out he model
	if args.singleModel:
		envvars['APOLLO_SINGLE_MODEL'] = 1
		envvars['APOLLO_REGION_MODEL'] = 0

#envvarsList = [var+'='+str(envvars[var]) for var in envvars]
#envvarsStr = " ".join(envvarsList)

print('Default environemnt vars set')

def convert_time_to_secs(slurm_time):
	hrs, mins, secs = slurm_time.split(':')

	return (int(hrs) * 60 * 60) + (int(mins) * 60) + (int(secs))

# Go through each problem size and policy of a particular benchmark
def doRunsForProg(prog):
	progsuffix = prog['suffix']
	#os.environ.update({'APOLLO_TRACE_CSV_FOLDER': prog['suffix']})

	exedir = prog['exedir']
	exe = prog['exe']
	exeprefix = prog['exeprefix']
	maxruntime = prog['maxruntime']
	datapath = prog['datapath']

	# Let's go to the executable directory
	os.chdir(exedir)

	for probSize in probSizes:

		inputArgs=prog[probSize]
		suffix = progsuffix+'-'+probSize

		# String replacement for full paths to input files
		if len(datapath) > 0:
			inputArgs = inputArgs%(exedir+'/'+datapath)

		if args.usePA:
			suffix = suffix+'-PA'

		for policy in policies:

			name = suffix[1:]
			envvars['APOLLO_TRACE_CSV_FOLDER_SUFFIX']=suffix
			envvars['APOLLO_POLICY_MODEL']=policy
			vars_to_use = {**os.environ.copy(), **envvars}
			#os.environ.update({'APOLLO_POLICY_MODEL': policy})
			#command = envvarsStr+' APOLLO_TRACE_CSV_FOLDER_SUFFIX='+suffix+' APOLLO_POLICY_MODEL='+policy
			#command = envvarsStr+' APOLLO_TRACE_CSV_FOLDER_SUFFIX='+suffix+' APOLLO_POLICY_MODEL='+policy
			#command = command+' '+debugRun+' '+exeprefix+' ./'+exe+inputArgs
			#command = command+' '+debugRun+' ./'+exe+inputArgs
			#command = command+' '+debugRun+' ./'+exe+inputArgs

			#command = 'sbatch -N 1 -n 1 --time="00:20:00" --output="'+suffix[1:]+'-runlogs.out" --open-mode=append --partition=pdebug --wrap="'+command+'"'
			#command = 'sbatch -N 1 -n 1 --time="'+maxruntime+'" --job-name="'+name+'" --output="'+name+'-runlogs.out" --open-mode=append --wrap="'+command+'"'
			#command = command+' '+debugRun+' --time="'+maxruntime+'" --job-name="'+name+'" --output="'+name+'-runlogs.out" --open-mode=append --wrap="./'+exe+inputArgs+'"'
			#command = debugRun+'--time="'+maxruntime+'" --job-name="'+name+'" --output="'+name+'-runlogs.out" --open-mode=append ./'+str(exe)+str(inputArgs)
			#command = debugRun+'--time="'+'00:05:00'+'" --job-name="'+name+'" --output="'+name+'-runlogs.out" --open-mode=append ./'+str(exe)+str(inputArgs)
			command = './'+str(exe)+str(inputArgs)

			print('Going to execute:', command)
			subprocess.call(shlex.split(command), env=vars_to_use)
	return


def main():
	print('Starting tests...')


	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	my_rank = comm.Get_rank()
	num_workers = size
	workers = range(num_workers)[1:]
	print('[%d] Starting!'%(my_rank))

	if my_rank == ROOT_RANK:
		todo = list(progs.keys())
		workerStates = {}

		# initialize the states
		for worker in workers:
			workerStates[worker] = (DONE_WORK_TAG, None)

		# while we still have work to do
		while len(todo) != 0 :
			# cycle through each worker and give them some work
			for worker in workerStates:
				workerState = workerStates[worker][0]
				workerReq = workerStates[worker][1]

				if workerState == DONE_WORK_TAG:
					if len(todo) != 0:
						work = todo.pop(0)
						req = comm.isend(work, dest=worker, tag=NEW_WORK_TAG)
						workerStates[worker] = (REQUEST_WORK_TAG, req)
				elif workerState == REQUEST_WORK_TAG:
					if workerReq.test():
						# if they were given work, let's wait for them to complete
						req = comm.irecv(source=worker, tag=DONE_WORK_TAG)
						workerStates[worker] = (NEW_WORK_TAG, req)
				elif workerState == NEW_WORK_TAG:
					# check if the work is done
					if workerReq.test():
						workerStates[worker] = (DONE_WORK_TAG, None)

		# when we run out of work, tell the workers to quit
		for worker in workers:
			req = comm.isend(None, dest=worker, tag=NEW_WORK_TAG)
			req.wait()

	# If we are not the ROOT node
	else:
			keepWorking = True
			mystate = DONE_WORK_TAG

			while keepWorking:
				if mystate == DONE_WORK_TAG:
					# Get some new work
					req = comm.irecv(source=ROOT_RANK, tag=NEW_WORK_TAG)
					mywork = req.wait()
					if mywork == None:
						print('[%d] DONE: ran out of work!'%(my_rank))
						break

					# Multiply by 3 since we're doing 3 policies
					max_time = convert_time_to_secs(progs[mywork]['maxruntime'])*len(policies)
					alive_time = time.time() - my_start_time
					if (alive_time + max_time) >= LIFETIME_IN_SECS:
						print('unable to continue, not enough time for %s, alive for %f[/%f] secs'%(mywork, alive_time, LIFETIME_IN_SECS))
						break

					print('[%d] I got work: %s'%(my_rank, mywork))
					# DO WORK HERE
					# DO WORK HERE
					# DO WORK HERE
					ete_xtime = time.time()
					doRunsForProg(progs[mywork])
					ete_xtime = time.time() - ete_xtime
					print('[%d] work completed in %f seconds!'%(my_rank, ete_xtime))
					req = comm.isend(mystate, dest=ROOT_RANK, tag=DONE_WORK_TAG)
					req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))


	return

main()