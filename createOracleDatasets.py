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
probSizes=['smallprob', 'medprob', 'largeprob']

def main():
	print('Starting oracle creation for each program...')
	print('Creating oracle for', hostname, 'in', rootdir)

	parser = argparse.ArgumentParser(
	    description='Launch static runs of benchmark programs using Apollo.')
	parser.add_argument('--usePA', action='store_true',
	                    help='Should we use PA data instead of VA?')
	parser.add_argument('--singlemodel', action='store_true',
	                    help='Should we make a single dataset model?')
	args = parser.parse_args()

	prognames = list(progs.keys())
	pava = 'VA'
	if args.usePA:
		pava = 'PA'

	# Go through each program
	for progname in prognames:
	#for progname in ['lulesh']:
		prog = progs[progname]
		exedir = rootdir+prog['exedir']
		progsuffix = prog['suffix'][1:]

		apollo_data_dir = exedir+'/'+progsuffix+'-data'
		
		# for each problem size, let's gather the traces to pass into the create-datasets script
		# we're going to create an oracle for each problem size. The create-datasets script
		# will create an optimal dataset for each region
		for probSize in probSizes:
			oracle_output_dir = apollo_data_dir+'/'+progsuffix+'-'+probSize+'-oracle-'+pava
			print('writing oracle output to:', oracle_output_dir)

			try:
				print('Making:', oracle_output_dir)
				os.mkdir(oracle_output_dir)
			except OSError as error:
				print('oracle dir may already exist, not creating...', error)

			# Go into the oracle folder since the create-datasets will dump here
			os.chdir(oracle_output_dir)

			#command = debugRun+' python3 '+create_dataset_script+' --agg mean-min --tracedirs'
			if args.singlemodel:
				command = 'python3 '+create_dataset_script+' --agg mean-min --singlemodel --tracedirs '
			else:
				command = 'python3 '+create_dataset_script+' --agg mean-min --tracedirs '

			# gather all the trial directories and add them to the command
			trialdirs = list(glob.glob('%s/%s-%s-trial*-%s-traces/' % (apollo_data_dir, progsuffix, probSize, pava)))
			for trialdir in trialdirs: 
				command += trialdir+' '

			print('Going to execute command:', command)
			print()
			os.system(command)

		# now let's make one oracle for the whole program using all the data across problem sizes
		oracle_output_dir = apollo_data_dir+'/'+progsuffix+'-allprobs-oracle-'+pava
		print('writing oracle output to:', oracle_output_dir)

		try:
			print('Making:', oracle_output_dir)
			os.mkdir(oracle_output_dir)
		except OSError as error:
			print('oracle dir may already exist, not creating...', error)
		os.chdir(oracle_output_dir)

		if args.singlemodel:
			command = 'python3 '+create_dataset_script+' --agg mean-min --singlemodel --tracedirs '
		else:
			command = 'python3 '+create_dataset_script+' --agg mean-min --tracedirs '
		trialdirs = list(glob.glob('%s/%s-*-trial*-%s-traces/' % (apollo_data_dir, progsuffix, pava)))
		for trialdir in trialdirs: 
			command += trialdir+' '
		print('Going to execute command:', command)
		print()
		os.system(command)


	print('Oracle Dataset Creation Job Completed!')
	return


main()