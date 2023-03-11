from mpi4py import MPI
import os
import subprocess, shlex
import argparse
from benchmarks import *
import sys
import time
import pandas as pd
from pathlib import Path
import itertools
import re

APOLLO_DATA_COLLECTION_DIR='/usr/WS2/bolet1/apolloDataCollection/dualKnobTestingViaPolicies'

rootdirs={
	'quartz': '/g/g15/bolet1/workspace/',
	'ruby': '/g/g15/bolet1/workspace/ruby/',
	'lassen': '/g/g15/bolet1/workspace/lassen/'
}

# This script assumes that you have logged-in to the target machine
# and have run 'source ~/.profile' to setup the envvars for the
# proper compiler. Then you can run this script.

hostname = os.uname()[1]
rootdir = ''
if 'quartz' in hostname:
	hostname='quartz'
elif 'ruby' in hostname:
	hostname='ruby'
else:
	hostname='lassen'
	hostname='quartz'

rootdir = rootdirs[hostname]

# These are the default number of trials we want to run for each configuration
NUM_TRIALS = 5
#NUM_TRIALS = 4

# These are the tags used by the MPI communicators
ROOT_RANK = 0
REQUEST_WORK_TAG = 11
ACK_WORK_TAG = 12
DONE_WORK_TAG = 13
NEW_WORK_TAG = 14

# Set the default env vars
envvars={
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
	'APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER':'0',
	'APOLLO_PERF_CNTRS_MLTPX':'0' ,
	'APOLLO_PERF_CNTRS':"PAPI_DP_OPS" ,
	'APOLLO_MIN_TRAINING_DATA':"0",
	'APOLLO_PERSISTENT_DATASETS':"0",
	'APOLLO_OUTPUT_DIR':"my-test",
	'APOLLO_DATASETS_DIR':"my-datasets",
	'APOLLO_TRACES_DIR':"my-traces",
	'APOLLO_MODELS_DIR':"my-models",
}

#depending on the hostname, lets set the thread count
# lassen is the default
if hostname == 'quartz':
	envvars['OMP_NUM_THREADS'] = '36'
elif hostname == 'ruby':
	envvars['OMP_NUM_THREADS'] = '56'
else:
	envvars['OMP_NUM_THREADS'] = '40'

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

class MPIJobScheduler:

	# Pass the output directory name to write to
	# Pass the exploration space elements as a dictionary
	def __init__(self, outputDir, csvDataFileName, **kwargs):
		self.outputDir = outputDir
		self.csvDataFileName = csvDataFileName
		self.explorSpace = kwargs
		return

	# go into the outputDir and read the CSV 
	# file to see what's been completed 
	def get_work_from_checkpoint(self):
		todo = list(itertools.product(*list(self.explorSpace.values())))
		#todo.sort()
		print('todo', len(todo))
		df = pd.DataFrame(columns=list(self.explorSpace.keys()) + ['eteXtime'])

		datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE

		#if the datafile exists, read from it
		if Path(datafilepath).exists():
			tempdf = pd.read_csv(datafilepath)

			# if we have more than 1 data point, let's remove items
			if tempdf.shape[0] > 0:
				# Based on what's already done, let's remove these elements from the todo list
				for row in tempdf.itertuples(index=False, name=None):
					trial = row[0:len(explorSpace.keys())]
					print('trial we have:', trial)
					if trial in todo:
						todo.remove(trial)

				# return the read-in dataframe
				return (todo, tempdf)

		return (todo, df)

	def preJobSetEnvVars(self):
		return

	class Manager:
		def __init__(self):
			return
	
	class Worker:
		def __init__(self):
			return


XTIME_FILE_PREFIX='threadCountAndPlacement'

parser = argparse.ArgumentParser(
    description='Launch counter variability runs of benchmark programs using Apollo.')
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

pava = 'VA'

threadCountOptions = 12
placementOptions = 2

policies = ['Static,policy='+str(i) for i in range(threadCountOptions*placementOptions)]
print('Using policies:', policies)

#policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2',
#					'Static,policy=3', 'Static,policy=4', 'Static,policy=5', 
#					'Static,policy=6', 'Static,policy=7']

#policies=['Static,policy=2']
#policies=['Static,policy=0', 'Static,policy=1']
#policies=['Static,policy=0']
#probSizes=['smallprob', 'medprob', 'largeprob']
probSizes=['medprob']

#threadPlaces = ['threads', 'cores', 'sockets', 'll_caches', 'numa_domains']
#threadPlaces = ['close', 'spread']
#cntrModes=['alwaysOn', 'uniqueFeat']
#countersToTry=['PAPI_DP_OPS', 'PAPI_SP_OPS', 'PAPI_LD_INS', 
#							 'PAPI_SR_INS', 'PAPI_LST_INS', 'PAPI_BR_INS',
#							 'PAPI_MEM_WCY', 'PAPI_L3_LDM', 'PAPI_RES_STL', 'PAPI_TOT_INS']
#countersToTry=[
#							 'PAPI_TOT_INS', 'PAPI_DP_OPS', 
#							 'PAPI_SP_OPS', 'PAPI_LD_INS', 
#							 'PAPI_SR_INS', 'PAPI_LST_INS', 
#							 'PAPI_BR_INS', 'PAPI_L3_LDM', 
#							 'PAPI_RES_STL' 
#							 ]

prognames = list(progs.keys())
#prognames =['lulesh']

if args.singleModel and not args.usePA:
	print('Cant use VA with single models... quitting...')
	sys.exit("Can't use VA with single models")

OUTPUT_XTIME_FILE = XTIME_FILE_PREFIX+'-ETE-XTimeData_VA.csv'

if args.usePA:
	envvars['APOLLO_ENABLE_PERF_CNTRS'] = '1'
	OUTPUT_XTIME_FILE = XTIME_FILE_PREFIX+'-ETE-XTimeData_PA.csv'
	pava = 'PA'

	if args.singleModel:
		envvars['APOLLO_SINGLE_MODEL'] = '1'
		envvars['APOLLO_REGION_MODEL'] = '0'

if args.makeTraces:
	envvars['APOLLO_TRACE_CSV'] = '1'
else:
	envvars['APOLLO_TRACE_CSV'] = '0'


NUM_TRIALS = args.numTrials
print('Doing %d trials'%(NUM_TRIALS))

if args.quickPolicies:
	policies= policies[0:9]
	print('policies quick:', policies)

print('Default environemnt vars set')


# This is the exploration space we will be considering
explorSpace = {
	'progname': list(progs.keys()),
	'probSize': probSizes,
	'policy': policies,
	'trialnum': list(range(NUM_TRIALS))
}

# This function will read the CSV file with data
# and then generate a list of trials yet to finish
def get_work_from_checkpoint():
	#todo = [(x,y,z,a,b,w) for x in prognames for y in probSizes for z in policies for a in countersToTry for b in cntrModes for w in range(NUM_TRIALS)]
	#todo = [(x,y,z,a,w) for x in prognames for y in probSizes for z in policies for a in threadPlaces for w in range(NUM_TRIALS)]
	todo = list(itertools.product(*list(explorSpace.values())))
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=list(explorSpace.keys()) + ['eteXtime'])

	datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE

	#if the datafile exists, read from it
	if Path(datafilepath).exists():
		tempdf = pd.read_csv(datafilepath)

		# if we have more than 1 data point, let's remove items
		if tempdf.shape[0] > 0:
			# Based on what's already done, let's remove these elements from the todo list
			for row in tempdf.itertuples(index=False, name=None):
				trial = row[0:len(explorSpace.keys())]
				print('trial we have:', trial)
				if trial in todo:
					todo.remove(trial)

			# return the read-in dataframe
			return (todo, tempdf)

	return (todo, df)


def doRunForProg(prog, probSize, policy, trialnum, mystdout, otherEnvvars):
	exedir = rootdir+prog['exedir']
	progsuffix = prog['suffix'][1:]

	exe = prog['exe']
	exeprefix = prog['exeprefix']
	datapath = prog['datapath']
	xtimeline = prog['xtimelinesearch']
	xtimescalefactor = float(prog['xtimescalefactor'])

	apollo_data_dir = exedir+'/'+progsuffix+'-data'
	envvars['APOLLO_OUTPUT_DIR'] = apollo_data_dir 

	apollo_trial_dir = progsuffix+'-'+probSize+'-'+('-'.join(str(item) for item in otherEnvvars))+'-'+XTIME_FILE_PREFIX+'-trial'+str(trialnum)+'-'+pava

	apollo_trace_dir = apollo_trial_dir + '-traces'
	apollo_dataset_dir = apollo_trial_dir + '-datasets'
	apollo_models_dir = apollo_trial_dir + '-models'
	
	envvars['APOLLO_TRACES_DIR'] = apollo_trace_dir
	envvars['APOLLO_DATASETS_DIR'] = apollo_dataset_dir
	envvars['APOLLO_MODELS_DIR'] = apollo_models_dir 

	for var, val in otherEnvvars.items():
		envvars[var] = val
	
	#envvars['APOLLO_PERF_CNTRS'] = papiCounter

	## if the cntrs should always run on each region execution
	#if cntrMode == cntrModes[0]:
		#envvars['APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER'] = '1'
	#else:
		#envvars['APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER'] = '0'


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
						#progname    = responseData[1][0]
						#probSize    = responseData[1][1]
						#policy      = responseData[1][2]
						#trialnum    = responseData[1][3]
						eteXtime    = responseData[2]

						otherData = dict(list(zip(list(explorSpace.keys()), responseData[1])))


						dataToAdd = {**otherData, **{'eteXtime': eteXtime}}
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

		stdoutFilename = APOLLO_DATA_COLLECTION_DIR+'/'+XTIME_FILE_PREFIX+'_stdout'+'/'+XTIME_FILE_PREFIX+'_stdout_rank'+str(my_rank)

		if args.usePA:		
			stdoutFilename += '_PA.txt'
		else:
			stdoutFilename += '_VA.txt'
		
		mystdout = open(stdoutFilename, 'a')

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
			# doRunForProg(prog, probSize, policy, trialnum, mystdout, otherEnvvars):
			otherEnvvars = dict(list(zip(list(explorSpace.keys())[4:], mywork[4:])))
			ete_xtime = doRunForProg(progs[mywork[0]], mywork[1], mywork[2], mywork[3], mystdout, otherEnvvars)
			mystdout.write('[%d] work completed in %f seconds!\n'%(my_rank, ete_xtime))
			req = comm.isend((DONE_WORK_TAG, mywork, ete_xtime), dest=ROOT_RANK, tag=DONE_WORK_TAG)
			req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))
		mystdout.close()
	return

main()