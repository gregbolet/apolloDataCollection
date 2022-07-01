from mpi4py import MPI
import os
import subprocess, shlex
import argparse
from benchmarks import progs
import sys
import time
import pandas as pd
import re
from pathlib import Path

# These are the default number of trials we want to run for each configuration
NUM_TRIALS = 10
#NUM_TRIALS = 4

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
	'APOLLO_TRACE_CSV':'0',
	'APOLLO_SINGLE_MODEL':'0' ,
	'APOLLO_REGION_MODEL':'1' ,
	'APOLLO_GLOBAL_TRAIN_PERIOD':'0',
	'APOLLO_ENABLE_PERF_CNTRS':'0' ,
	'APOLLO_PERF_CNTRS_MLTPX':'0' ,
	'APOLLO_PERF_CNTRS':"PAPI_DP_OPS,PAPI_TOT_INS" ,
	'APOLLO_MIN_TRAINING_DATA':"0",
	'APOLLO_PERSISTENT_DATASETS':"0",
	'APOLLO_OUTPUT_DIR':"my-test",
	'APOLLO_DATASETS_DIR':"my-datasets",
	'APOLLO_TRACES_DIR':"my-traces",
	'APOLLO_MODELS_DIR':"my-models",
}

minTrainData=[3,6,9,12,15,18,21,24,27,30]
policies=['DecisionTree,max_depth=4,explore=RoundRobin', 'DecisionTree,max_depth=4,explore=Random']
probSizes=['smallprob', 'medprob', 'largeprob']
prognames = list(progs.keys())

parser = argparse.ArgumentParser(
    description='Launch static runs of benchmark programs using Apollo.')
parser.add_argument('--usePA', action='store_true',
                    help='Should we use PA data instead of VA?')
parser.add_argument('--makeTraces', action='store_true',
                    help='Should we store CSV traces?')
parser.add_argument('--singleModel', action='store_true',
                    help='Should we execute with single models for PA?')
parser.add_argument('--quickPolicies', action='store_true',
                    help='Should we just do policies 0 and 1 for quick results.')
parser.add_argument('--numTrials', help='How many trials to run with', default=10,
                    type=int)

args = parser.parse_args()
print('I got args:', args)

if args.singleModel and not args.usePA:
	print('Cant use VA with single models... quitting...')
	sys.exit("Can't use VA with single models")

OUTPUT_XTIME_FILE='online-ETE-XTimeData_VA.csv'

if args.usePA:
	envvars['APOLLO_ENABLE_PERF_CNTRS'] = '1'
	OUTPUT_XTIME_FILE='online-ETE-XTimeData_PA.csv'
	# This flag is useless, we make the oracle from the region trace csvs
	# these flags are only useful if we have Apollo print out he model
	if args.singleModel:
		envvars['APOLLO_SINGLE_MODEL'] = '1'
		envvars['APOLLO_REGION_MODEL'] = '0'

if args.makeTraces:
	envvars['APOLLO_TRACE_CSV'] = '1'
else:
	envvars['APOLLO_TRACE_CSV'] = '0'

if args.quickPolicies:
	policies= policies[0:2]
	print('policies quick:', policies)

NUM_TRIALS = args.numTrials
print('Doing %d trials'%(NUM_TRIALS))

#envvarsList = [var+'='+str(envvars[var]) for var in envvars]
#envvarsStr = " ".join(envvarsList)

print('Default environemnt vars set')

# This function will read the CSV file with data
# and then generate a list of trials yet to finish
def get_work_from_checkpoint():
	todo = [(x,y,z,v,w) for x in prognames for y in probSizes for z in policies for v in minTrainData for w in range(NUM_TRIALS)]
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=['progname', 'probSize', 'policy', 'minTrainData', 'trialnum', 'eteXtime'])

	datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE

	#if the datafile exists, read from it
	if Path(datafilepath).exists():
		tempdf = pd.read_csv(datafilepath)

		# if we have more than 1 data point, let's remove items
		if tempdf.shape[0] > 0:
			# Based on what's already done, let's remove these elements from the todo list
			for row in tempdf.itertuples(index=False, name=None):
				trial = row[0:5]
				print('trial we have:', trial)
				if trial in todo:
					todo.remove(trial)

			# return the read-in dataframe
			return (todo, tempdf)

	return (todo, df)

# open and go through a file to get the last occurence of line
# with a particular substring. We then search this line for 
# a floating point xtime value and return that
def get_file_last_line_timing_match(filename, line_substring):

	lines = []
	with open(filename, 'r') as toread:
		for line in toread:
			if line_substring in line:
				lines.append(line)

	if len(lines) > 0:
		# now get the last line
		last_line = lines[len(lines)-1]
		floats = re.findall(r"[-|+]?\d*\.?\d*[e|E]?[+|-]?\d+", last_line)

		# if we have a nonzero count of floats
		# grab the first one and use that as the timing value
		if len(floats) > 0:
			return float(floats[0])

	return None


def doRunForProg(prog, probSize, policy, minTrainData, trialnum, mystdout):
	progsuffix = prog['suffix']
	exedir = prog['exedir']
	exe = prog['exe']
	exeprefix = prog['exeprefix']
	maxruntime = prog['maxruntime']
	datapath = prog['datapath']
	xtimeline = prog['xtimelinesearch']
	xtimescalefactor = float(prog['xtimescalefactor'])

	envvars['APOLLO_MIN_TRAINING_DATA'] = str(minTrainData)

	apollo_output_dir = progsuffix[1:]+'-online-data'
	envvars['APOLLO_OUTPUT_DIR'] = apollo_output_dir

	apollo_trial_dir = progsuffix[1:]+'-'+probSize+'-trial'+str(trialnum)

	if args.usePA:
		apollo_trial_dir += '-PA'
	else:
		apollo_trial_dir += '-VA'

	apollo_trace_dir = apollo_trial_dir + '-traces'
	apollo_dataset_dir = apollo_trial_dir + '-datasets'
	apollo_models_dir = apollo_trial_dir + '-models'
	
	envvars['APOLLO_TRACES_DIR'] = apollo_trace_dir
	envvars['APOLLO_DATASETS_DIR'] = apollo_dataset_dir
	envvars['APOLLO_MODELS_DIR'] = apollo_models_dir


	# Let's go to the executable directory
	os.chdir(exedir)

	inputArgs=prog[probSize]

	# String replacement for full paths to input files
	if len(datapath) > 0:
		# count the number of replacements to make
		numtorep = inputArgs.count('%s')
		strtorep = exedir+'/'+datapath
		replTuple = tuple([strtorep]*numtorep)
		inputArgs = inputArgs%replTuple

	envvars['APOLLO_POLICY_MODEL']=policy
	vars_to_use = {**os.environ.copy(), **envvars}

	command = exeprefix+'./'+str(exe)+str(inputArgs)

	mystdout.write('using envvars:\n' + str(envvars) + '\n')
	mystdout.write('Going to execute:'+str(command)+'\n')
	# Get the end-to-end xtime
	#ete_xtime = time.time()
	ete_xtime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
	subprocess.call(shlex.split(command), env=vars_to_use, stdout=mystdout, stderr=mystdout)
	ete_xtime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - ete_xtime

	mystdout.flush()

	# now let's see if we can get the xtime from the stdout
	if xtimeline != '':
		file_xtime = get_file_last_line_timing_match(mystdout.name, xtimeline)
		if file_xtime != None:
			return file_xtime*xtimescalefactor

	return ete_xtime*xtimescalefactor

def main():
	print('Starting tests...')

	#os.chdir(APOLLO_DATA_COLLECTION_DIR)

	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	my_rank = comm.Get_rank()
	num_workers = size
	workers = range(num_workers)[1:]
	print('[%d] Starting!'%(my_rank))

	print('num workers: ', num_workers)

	if my_rank == ROOT_RANK:
		workerStates = {}

		# initialize the states
		for worker in workers:
			workerStates[worker] = (DONE_WORK_TAG, None)

		# prepare the work to do
		todo, df = get_work_from_checkpoint()

		# while we still have work to do
		while True:

			# check for stopping condition
			if len(todo) == 0:
				# check that all the workers have a DONE_WORK_TAG
				doneworkCount = 0
				numworkers = 0
				for worker in workerStates:
					numworkers += 1
					if workerStates[worker][0] == DONE_WORK_TAG:
						doneworkCount += 1
				
				# if all the workers are waiting and there is no more work, we quit
				if doneworkCount == numworkers:
					break

			#print('TODO is NOT empty! ')
			# cycle through each worker and give them some work
			for worker in workerStates:
				workerState = workerStates[worker][0]
				workerReq = workerStates[worker][1]

				# If they finished their work, give them new work
				if workerState == DONE_WORK_TAG:
					#print('DONE_WORK_TAG')
					if len(todo) != 0:
						work = todo.pop(0)
						print('Gonna work on: ', work)
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
						progname 		 = responseData[1][0]
						probSize 		 = responseData[1][1]
						policy   		 = responseData[1][2]
						mintraindata = responseData[1][3]
						trialnum     = responseData[1][4]
						eteXtime     = responseData[2]
						dataToAdd = {'progname': progname, 'probSize': probSize,
												 'policy': policy, 'minTrainData':mintraindata,
												 'trialnum': trialnum, 'eteXtime': eteXtime}
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

		if args.usePA:		
			mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/online_mpi_stdout_rank'+str(my_rank)+'_PA.txt', 'a')
		else:
			mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/online_mpi_stdout_rank'+str(my_rank)+'_VA.txt', 'a')

		# redirect my stdout to use this new file
		#sys.stdout = mystdout

		while True:
			# Get some new work
			req = comm.irecv(source=ROOT_RANK, tag=NEW_WORK_TAG)
			mywork = req.wait()
			if mywork == None:
				mystdout.write('[%d] DONE: ran out of work!\n'%(my_rank))
				break

			mystdout.write('[%d] I got work: %s\n'%(my_rank, mywork))
			# DO WORK HERE
			# DO WORK HERE
			# DO WORK HERE
			# write to the output file so we know what run this was
			#mystdout.write('PERFORMING TEST FOR: '+str(mywork)+'\n')	
			ete_xtime = doRunForProg(progs[mywork[0]], mywork[1], mywork[2], mywork[3], mywork[4], mystdout)
			mystdout.write('[%d] work completed in %f seconds!\n'%(my_rank, ete_xtime))
			req = comm.isend((DONE_WORK_TAG, mywork, ete_xtime), dest=ROOT_RANK, tag=DONE_WORK_TAG)
			req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))
		mystdout.close()
	return

main()