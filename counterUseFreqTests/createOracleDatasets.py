#!/usr/tce/packages/python/python-3.8.2/bin/python3

import argparse
import os
import subprocess
from new_benchmarks import *
import glob

# This program will run each of the benchmarks in the static0, static1, static2
# policies. This will allow us to then parse the TRACE_CSV files to quantify
# whether there is potential for speedup by adjusting thread counts

create_dataset_script='/g/g15/bolet1/workspace/apollo/src/python/modeling/create-dataset.py'

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']
#probSizes=['smallprob', 'medprob', 'largeprob']
probSizes=['medprob']
cntrModes=['alwaysOn', 'uniqueFeat']

countersToTry=[
							 'PAPI_TOT_INS', 'PAPI_DP_OPS', 
							 'PAPI_SP_OPS', 'PAPI_LD_INS', 
							 'PAPI_SR_INS', 'PAPI_LST_INS', 
							 'PAPI_BR_INS', 'PAPI_L3_LDM', 
							 'PAPI_RES_STL' 
							 ]

def main():
	print('Starting oracle creation for each program...')
	print('Creating oracle for', hostname, 'in', rootdir)

	parser = argparse.ArgumentParser(
	    description='Launch static runs of benchmark programs using Apollo.')
	parser.add_argument('--usePA', action='store_true',
	                    help='Should we use PA data instead of VA?')
	parser.add_argument('--singlemodel', action='store_true',
	                    help='Should we make a single dataset model?')
	parser.add_argument('-b', '--benchmarks', nargs='+', default=[], 
											help='what benchmarks to create datasets for?')
	parser.add_argument('-k', '--colsToKeep', nargs='+', default=[], 
											help='What feature columns to keep when creating a dataset?')
	args = parser.parse_args()

	if len(args.benchmarks) == 0:
		prognames = list(progs.keys())
	else:
		prognames = args.benchmarks


	pava = 'VA'
	if args.usePA:
		pava = 'PA'

	# Go through each program
	for progname in prognames:
	#for progname in ['nas_bt']:
		prog = progs[progname]
		exedir = rootdir+prog['exedir']
		progsuffix = prog['suffix'][1:]

		apollo_data_dir = exedir+'/'+progsuffix+'-data'
		
		# for each problem size, let's gather the traces to pass into the create-datasets script
		# we're going to create an oracle for each problem size. The create-datasets script
		# will create an optimal dataset for each region
		for probSize in probSizes:

			for cntrMode in cntrModes:

				# We're going to make an oracle model for each counter in each counter mode
				for counter in countersToTry:
					oracle_output_dir = apollo_data_dir+'/'+progsuffix+'-'+probSize+'-'+counter+'-ORACLE-'+cntrMode+'-'+pava
					print('writing oracle output to:', oracle_output_dir)

					try:
						print('Making:', oracle_output_dir)
						os.mkdir(oracle_output_dir)
					except OSError as error:
						print('oracle dir may already exist, not creating...', error)

					# Go into the oracle folder since the create-datasets will dump here
					os.chdir(oracle_output_dir)

					#command = debugRun+' python3 '+create_dataset_script+' --agg mean-min --tracedirs'
					command = 'python3 '+create_dataset_script+' --agg mean-min '
					if args.singlemodel:
						command += '--singlemodel '

					if len(args.colsToKeep) != 0:
						command += '--colsToKeep '+' '.join(args.colsToKeep)+' '

					command += '--tracedirs '
					# gather all the trial directories and add them to the command
					trialdirs = list(glob.glob('%s/%s-%s-%s-%s-*trial*-%s-traces/' % (apollo_data_dir, progsuffix, probSize, counter, cntrMode, pava)))
					for trialdir in trialdirs: 
						command += trialdir+' '

					print('Going to execute command:', command)
					print()
					os.system(command)


	print('Oracle Dataset Creation Job Completed!')
	return


main()