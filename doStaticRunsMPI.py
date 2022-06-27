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

my_start_time = time.time()

# Assuming 3 hours max time for each MPI node for now
LIFETIME_IN_SECS = 5 * 60 * 60

# These are the number of trials we want to run for each configuration
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
	'APOLLO_TRACE_CSV_FOLDER_SUFFIX':"-test",
}

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']
#policies=['Static,policy=2']
#policies=['Static,policy=0', 'Static,policy=1']
#policies=['Static,policy=0']
#debugRun='srun --partition=pdebug -n1 -N1 --export=ALL '
#debugRun='srun -n1 -N1 --export=ALL '
probSizes=['smallprob', 'medprob', 'largeprob']
#probSizes=['smallprob']
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

OUTPUT_XTIME_FILE='static-ETE-XTimeData_VA.csv'

if args.usePA:
	envvars['APOLLO_ENABLE_PERF_CNTRS'] = '1'
	OUTPUT_XTIME_FILE='static-ETE-XTimeData_PA.csv'
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
	todo = [(x,y,z,w) for x in prognames for y in probSizes for z in policies for w in range(NUM_TRIALS)]
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=['progname', 'probSize', 'policy', 'trialnum', 'eteXtime'])

	datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE

	#if the datafile exists, read from it
	if Path(datafilepath).exists():
		tempdf = pd.read_csv(datafilepath)

		# if we have more than 1 data point, let's remove items
		if tempdf.shape[0] > 0:
			# Based on what's already done, let's remove these elements from the todo list
			for row in tempdf.itertuples(index=False, name=None):
				trial = row[0:4]
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

def convert_time_to_secs(slurm_time):
	hrs, mins, secs = slurm_time.split(':')

	return (int(hrs) * 60 * 60) + (int(mins) * 60) + (int(secs))

def doRunForProg(prog, probSize, policy, trialnum, mystdout):
	progsuffix = prog['suffix']
	exedir = prog['exedir']
	exe = prog['exe']
	exeprefix = prog['exeprefix']
	maxruntime = prog['maxruntime']
	datapath = prog['datapath']
	xtimeline = prog['xtimelinesearch']
	xtimescalefactor = float(prog['xtimescalefactor'])

	# Let's go to the executable directory
	os.chdir(exedir)

	inputArgs=prog[probSize]
	suffix = progsuffix+'-'+probSize+'-trial'+str(trialnum)

	# String replacement for full paths to input files
	if len(datapath) > 0:
		# count the number of replacements to make
		numtorep = inputArgs.count('%s')
		strtorep = exedir+'/'+datapath
		replTuple = tuple([strtorep]*numtorep)
		inputArgs = inputArgs%replTuple

	if args.usePA:
		suffix = suffix+'-PA'

	envvars['APOLLO_TRACE_CSV_FOLDER_SUFFIX']=suffix
	envvars['APOLLO_POLICY_MODEL']=policy
	vars_to_use = {**os.environ.copy(), **envvars}

	command = exeprefix+'./'+str(exe)+str(inputArgs)

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

		if args.usePA:		
			mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/mpi_stdout_rank'+str(my_rank)+'_PA.txt', 'a')
		else:
			mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/mpi_stdout_rank'+str(my_rank)+'_VA.txt', 'a')

		# redirect my stdout to use this new file
		#sys.stdout = mystdout

		while True:
			# Get some new work
			req = comm.irecv(source=ROOT_RANK, tag=NEW_WORK_TAG)
			mywork = req.wait()
			if mywork == None:
				mystdout.write('[%d] DONE: ran out of work!\n'%(my_rank))
				break

			max_time = convert_time_to_secs(progs[mywork[0]]['maxruntime'])
			alive_time = time.time() - my_start_time
			if (alive_time + max_time) >= LIFETIME_IN_SECS:
				mystdout.write('may be unable to continue, not enough time for %s, alive for %f[/%f] secs\n'%(mywork, alive_time, LIFETIME_IN_SECS))

			mystdout.write('[%d] I got work: %s\n'%(my_rank, mywork))
			# DO WORK HERE
			# DO WORK HERE
			# DO WORK HERE
			# write to the output file so we know what run this was
			#mystdout.write('PERFORMING TEST FOR: '+str(mywork)+'\n')	
			ete_xtime = doRunForProg(progs[mywork[0]], mywork[1], mywork[2], mywork[3], mystdout)
			mystdout.write('[%d] work completed in %f seconds!\n'%(my_rank, ete_xtime))
			req = comm.isend((DONE_WORK_TAG, mywork, ete_xtime), dest=ROOT_RANK, tag=DONE_WORK_TAG)
			req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))
		mystdout.close()
	return

main()