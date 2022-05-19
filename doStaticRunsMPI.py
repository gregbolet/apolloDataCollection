from mpi4py import MPI
import os
import subprocess, shlex
import argparse
from benchmarks import progs
import sys
import time
import pandas as pd

my_start_time = time.time()

# Assuming 3 hours max time for each MPI node for now
LIFETIME_IN_SECS = 3 * 60 * 60

# These are the number of trials we want to run for each configuration
NUM_TRIALS = 10

OUTPUT_XTIME_FILE='static-ETE-XTimeData.csv'

ROOT_RANK = 0
REQUEST_WORK_TAG = 11
ACK_WORK_TAG = 12
DONE_WORK_TAG = 13
NEW_WORK_TAG = 14

APOLLO_DATA_COLLECTION_DIR='/usr/WS2/bolet1/apolloDataCollection'

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
prognames = list(progs.keys())

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

# This function will read the CSV file with data
# and then generate a list of trials yet to finish
def get_work_from_checkpoint():
	todo = [(x,y,z,w) for x in prognames for y in probSizes for z in policies for w in range(NUM_TRIALS)]
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=['progname', 'probSize', 'policy', 'trialnum', 'eteXtime'])

	#if the datafile exists, read from it
	tempdf = pd.read_csv(APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE)

	# if we have more than 1 data point, let's remove items
	if tempdf.shape[0] > 0:
		# Based on what's already done, let's remove these elements from the todo list
		for row in tempdf.itertuples(index=False, name=None):
			trial = row[0:4]
			print('trial we have:', trial)
			if trial in todo:
				todo.remove(trial)
		
		return (todo, tempdf)

	return (todo, df)

def convert_time_to_secs(slurm_time):
	hrs, mins, secs = slurm_time.split(':')

	return (int(hrs) * 60 * 60) + (int(mins) * 60) + (int(secs))

def doRunForProg(prog, probSize, policy, mystdout):
	progsuffix = prog['suffix']
	exedir = prog['exedir']
	exe = prog['exe']
	exeprefix = prog['exeprefix']
	maxruntime = prog['maxruntime']
	datapath = prog['datapath']

	# Let's go to the executable directory
	os.chdir(exedir)

	inputArgs=prog[probSize]
	suffix = progsuffix+'-'+probSize

	# String replacement for full paths to input files
	if len(datapath) > 0:
		inputArgs = inputArgs%(exedir+'/'+datapath)

	if args.usePA:
		suffix = suffix+'-PA'

	name = suffix[1:]
	envvars['APOLLO_TRACE_CSV_FOLDER_SUFFIX']=suffix
	envvars['APOLLO_POLICY_MODEL']=policy
	vars_to_use = {**os.environ.copy(), **envvars}

	command = './'+str(exe)+str(inputArgs)

	print('Going to execute:', command)
	# Get the end-to-end xtime
	ete_xtime = time.time()
	subprocess.call(shlex.split(command), env=vars_to_use, stdout=mystdout)
	ete_xtime = time.time() - ete_xtime

	return ete_xtime

def main():
	print('Starting tests...')

	#os.chdir(APOLLO_DATA_COLLECTION_DIR)

	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	my_rank = comm.Get_rank()
	num_workers = size
	workers = range(num_workers)[1:]
	print('[%d] Starting!'%(my_rank))

	if my_rank == ROOT_RANK:
		workerStates = {}

		# initialize the states
		for worker in workers:
			workerStates[worker] = (DONE_WORK_TAG, None)

		# prepare the work to do
		todo, df = get_work_from_checkpoint()

		# Only do the first few experiments for testing purposes
		#todo = todo[:25]

		# while we still have work to do
		while len(todo) != 0 :
			# cycle through each worker and give them some work
			for worker in workerStates:
				workerState = workerStates[worker][0]
				workerReq = workerStates[worker][1]

				# If they finished their work, give them new work
				if workerState == DONE_WORK_TAG:
					#print('DONE_WORK_TAG')
					if len(todo) != 0:
						work = todo.pop(0)
						req = comm.isend(work, dest=worker, tag=NEW_WORK_TAG)
						workerStates[worker] = (REQUEST_WORK_TAG, req)
				elif workerState == REQUEST_WORK_TAG:
					#print('REQUEST_WORK_TAG')
					if workerReq.test():
						# let's set up the response testing object
						req = comm.irecv(source=worker, tag=DONE_WORK_TAG)
						workerStates[worker] = (NEW_WORK_TAG, req)
				elif workerState == NEW_WORK_TAG:
					#print('NEW_WORK_TAG')
					# check if the work is done
					isDone, responseData = workerReq.test()
					if isDone:
						print('worker completed with message: ', responseData)
						progname = responseData[1][0]
						probSize = responseData[1][1]
						policy   = responseData[1][2]
						trialnum = responseData[1][3]
						eteXtime = responseData[2]
						dataToAdd = {'progname': progname, 'probSize': probSize,
												 'policy': policy, 'trialnum': trialnum,
												 'eteXtime': eteXtime}
						toAppend = pd.DataFrame([dataToAdd])
						df = pd.concat([df, toAppend], ignore_index=True)
						df.to_csv(OUTPUT_XTIME_FILE, index=False)
						workerStates[worker] = (DONE_WORK_TAG, None)

		# when we run out of work, tell the workers to quit
		for worker in workers:
			req = comm.isend(None, dest=worker, tag=NEW_WORK_TAG)
			req.wait()

	# If we are not the ROOT node
	else:
		mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/mpi_stdout_rank'+str(my_rank)+'.txt', 'a')

		while True:
			# Get some new work
			req = comm.irecv(source=ROOT_RANK, tag=NEW_WORK_TAG)
			mywork = req.wait()
			if mywork == None:
				print('[%d] DONE: ran out of work!'%(my_rank))
				break

			max_time = convert_time_to_secs(progs[mywork[0]]['maxruntime'])
			alive_time = time.time() - my_start_time
			if (alive_time + max_time) >= LIFETIME_IN_SECS:
				print('unable to continue, not enough time for %s, alive for %f[/%f] secs'%(mywork, alive_time, LIFETIME_IN_SECS))
				break

			print('[%d] I got work: %s'%(my_rank, mywork))
			# DO WORK HERE
			# DO WORK HERE
			# DO WORK HERE
			ete_xtime = doRunForProg(progs[mywork[0]], mywork[1], mywork[2], mystdout)
			print('[%d] work completed in %f seconds!'%(my_rank, ete_xtime))
			req = comm.isend((DONE_WORK_TAG, mywork, ete_xtime, mywork[3]), dest=ROOT_RANK, tag=DONE_WORK_TAG)
			req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))
	return

main()