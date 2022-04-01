#!/usr/tce/packages/python/python-3.8.2/bin/python3

import os
import subprocess
import argparse
from benchmarks import progs

# This program will run each of the benchmarks in the static0, static1, static2
# policies. This will allow us to then parse the TRACE_CSV files to quantify
# whether there is potential for speedup by adjusting thread counts

envvars={
	'OMP_NUM_THREADS':36,
	'OMP_WAIT_POLICY':"active",
	'OMP_PROC_BIND':"close",
	'OMP_PLACES':"cores",
	'APOLLO_COLLECTIVE_TRAINING':0 ,
	'APOLLO_LOCAL_TRAINING':1 ,
	'APOLLO_RETRAIN_ENABLE':0 ,
	'APOLLO_STORE_MODELS':0,
	'APOLLO_TRACE_CSV':1,
	'APOLLO_SINGLE_MODEL':0 ,
	'APOLLO_REGION_MODEL':1 ,
	'APOLLO_GLOBAL_TRAIN_PERIOD':10000,
	'APOLLO_ENABLE_PERF_CNTRS':0 ,
	'APOLLO_PERF_CNTRS_MLTPX':0 ,
	'APOLLO_PERF_CNTRS':"PAPI_DP_OPS,PAPI_TOT_INS" ,
	'APOLLO_TRACE_CSV_FOLDER_SUFFIX':"-test",
}


#debugRun='srun --partition=pdebug -n1 -N1 --export=ALL '
debugRun='srun -n1 -N1 --export=ALL '
probSizes=['smallprob', 'medprob', 'largeprob']

def main():
	print('Starting oracle creation for each program...')

	parser = argparse.ArgumentParser(
	    description='Launch static runs of benchmark programs using Apollo.')
	parser.add_argument('--usePA', action='store_true',
	                    help='Should we use PA data instead of VA?')
	args = parser.parse_args()

	if args.usePA:
		envvars['APOLLO_ENABLE_PERF_CNTRS'] = 1

	envvarsList = [var+'='+str(envvars[var]) for var in envvars]
	envvarsStr = " ".join(envvarsList)

	# Run each program without performance counters enabled
	for progname in progs:
		prog = progs[progname]
		progsuffix = prog['suffix']
		#os.environ.update({'APOLLO_TRACE_CSV_FOLDER': prog['suffix']})

		exedir = prog['exedir']
		exe = prog['exe']
		exeprefix = prog['exeprefix']
		maxruntime = prog['maxruntime']
		datapath = prog['datapath']

		# Let's go to the executable directory
		os.chdir(exedir)
		oraclepath = exedir+'/'+progsuffix[1:]

		if args.usePA:
			oraclepath += '-PA-oracle'
		else:
			oraclepath += '-VA-oracle'

		# Go into the oracle folder since the create-datasets will dump here
		# and the load-datasets will read from here
		os.chdir(oraclepath)

		#command = debugRun+' python3 '+create_dataset_script+' --agg mean-min --tracedirs'

		for probSize in probSizes:

			inputArgs=prog[probSize]

			# String replacement for full paths to input files
			if len(datapath) > 0:
				inputArgs = inputArgs%(exedir+'/'+datapath)

			suffix = progsuffix+'-'+probSize

			if args.usePA:
				suffix = suffix+'-PA'

			name = suffix[1:]

			command = envvarsStr+' APOLLO_POLICY_MODEL=DecisionTree,load-dataset,max_depth=4'+' APOLLO_TRACE_CSV_FOLDER_SUFFIX='+suffix
			#command = command+' '+debugRun+' '+exeprefix+' ./'+exe+inputArgs
			command = command+' '+debugRun+' ../'+exe+inputArgs

			command = 'sbatch -N 1 -n 1 --time="'+maxruntime+'" --job-name="'+name+'oracle" --output="'+name+'-oracle-runlogs.out" --open-mode=append --wrap="'+command+'"'
			print('Going to execute:', command)
			os.system(command)

	print('Static runs launched!')
	return


main()