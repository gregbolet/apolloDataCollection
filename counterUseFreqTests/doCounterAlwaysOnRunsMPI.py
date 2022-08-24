from mpi4py import MPI
import os
import subprocess, shlex
import argparse
from new_benchmarks import *
import sys
import time
import pandas as pd
from pathlib import Path

XTIME_FILE_PREFIX='cntrVariab'

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

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']
#policies=['Static,policy=2']
#policies=['Static,policy=0', 'Static,policy=1']
#policies=['Static,policy=0']
#probSizes=['smallprob', 'medprob', 'largeprob']
probSizes=['medprob']

cntrModes=['alwaysOn', 'uniqueFeat']
#countersToTry=['PAPI_DP_OPS', 'PAPI_SP_OPS', 'PAPI_LD_INS', 
#							 'PAPI_SR_INS', 'PAPI_LST_INS', 'PAPI_BR_INS',
#							 'PAPI_MEM_WCY', 'PAPI_L3_LDM', 'PAPI_RES_STL', 'PAPI_TOT_INS']
countersToTry=[
							 'PAPI_TOT_INS', 'PAPI_DP_OPS', 
							 'PAPI_SP_OPS', 'PAPI_LD_INS', 
							 'PAPI_SR_INS', 'PAPI_LST_INS', 
							 'PAPI_BR_INS', 'PAPI_L3_LDM', 
							 'PAPI_RES_STL' 
							 ]

#prognames = list(progs.keys())
prognames =['nas_ft', 'rodinia_cfd', 'nas_sp']

if args.singleModel and not args.usePA:
	print('Cant use VA with single models... quitting...')
	sys.exit("Can't use VA with single models")

OUTPUT_XTIME_FILE = XTIME_FILE_PREFIX+'-ETE-XTimeData_VA.csv'

if args.usePA:
	envvars['APOLLO_ENABLE_PERF_CNTRS'] = '1'
	OUTPUT_XTIME_FILE = XTIME_FILE_PREFIX+'-ETE-XTimeData_PA.csv'
	pava = 'PA'

	# This flag is useless, we make the oracle from the region trace csvs
	# these flags are only useful if we have Apollo print out he model
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
	policies= policies[0:2]
	print('policies quick:', policies)

#envvarsList = [var+'='+str(envvars[var]) for var in envvars]
#envvarsStr = " ".join(envvarsList)

print('Default environemnt vars set')

# This function will read the CSV file with data
# and then generate a list of trials yet to finish
def get_work_from_checkpoint():
	todo = [(x,y,z,a,b,w) for x in prognames for y in probSizes for z in policies for a in countersToTry for b in cntrModes for w in range(NUM_TRIALS)]
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=['progname', 'probSize', 'policy', 'papiCounter', 'cntrMode', 'trialnum', 'eteXtime'])

	datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+OUTPUT_XTIME_FILE

	#if the datafile exists, read from it
	if Path(datafilepath).exists():
		tempdf = pd.read_csv(datafilepath)

		# if we have more than 1 data point, let's remove items
		if tempdf.shape[0] > 0:
			# Based on what's already done, let's remove these elements from the todo list
			for row in tempdf.itertuples(index=False, name=None):
				trial = row[0:6]
				print('trial we have:', trial)
				if trial in todo:
					todo.remove(trial)

			# return the read-in dataframe
			return (todo, tempdf)

	return (todo, df)


def doRunForProg(prog, probSize, policy, papiCounter, cntrMode, trialnum, mystdout):
	exedir = rootdir+prog['exedir']
	progsuffix = prog['suffix'][1:]

	exe = prog['exe']
	exeprefix = prog['exeprefix']
	datapath = prog['datapath']
	xtimeline = prog['xtimelinesearch']
	xtimescalefactor = float(prog['xtimescalefactor'])

	apollo_data_dir = exedir+'/'+progsuffix+'-data'
	envvars['APOLLO_OUTPUT_DIR'] = apollo_data_dir 

	apollo_trial_dir = progsuffix+'-'+probSize+'-'+papiCounter+'-'+cntrMode+'-'+XTIME_FILE_PREFIX+'-trial'+str(trialnum)+'-'+pava

	apollo_trace_dir = apollo_trial_dir + '-traces'
	apollo_dataset_dir = apollo_trial_dir + '-datasets'
	apollo_models_dir = apollo_trial_dir + '-models'
	
	envvars['APOLLO_TRACES_DIR'] = apollo_trace_dir
	envvars['APOLLO_DATASETS_DIR'] = apollo_dataset_dir
	envvars['APOLLO_MODELS_DIR'] = apollo_models_dir 

	envvars['APOLLO_PERF_CNTRS'] = papiCounter

	# if the cntrs should always run on each region execution
	if cntrMode == cntrModes[0]:
		envvars['APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER'] = '1'
	else:
		envvars['APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER'] = '0'


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
						progname    = responseData[1][0]
						probSize    = responseData[1][1]
						policy      = responseData[1][2]
						papiCounter = responseData[1][3]
						cntrMode    = responseData[1][4]
						trialnum    = responseData[1][5]
						eteXtime    = responseData[2]
						dataToAdd = {'progname': progname, 'probSize': probSize,
												 'policy': policy, 'papiCounter': papiCounter, 
												 'cntrMode': cntrMode, 'trialnum': trialnum, 
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
			ete_xtime = doRunForProg(progs[mywork[0]], mywork[1], mywork[2], mywork[3], mywork[4], mywork[5], mystdout)
			mystdout.write('[%d] work completed in %f seconds!\n'%(my_rank, ete_xtime))
			req = comm.isend((DONE_WORK_TAG, mywork, ete_xtime), dest=ROOT_RANK, tag=DONE_WORK_TAG)
			req.wait()



			#command = 'grep -rni "launched"'
			# try to launch a command
			#subprocess.call(shlex.split(command))
		mystdout.close()
	return

main()