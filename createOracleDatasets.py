#!/usr/tce/packages/python/python-3.8.2/bin/python3

import argparse
import os
import subprocess
from benchmarks import progs

# This program will run each of the benchmarks in the static0, static1, static2
# policies. This will allow us to then parse the TRACE_CSV files to quantify
# whether there is potential for speedup by adjusting thread counts

create_dataset_script='/g/g15/bolet1/workspace/apollo/src/python/modeling/create-dataset.py'

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']

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

	# Run each program without performance counters enabled
	for progname in progs:
		prog = progs[progname]
		progsuffix = prog['suffix']
		#os.environ.update({'APOLLO_TRACE_CSV_FOLDER': prog['suffix']})

		exedir = prog['exedir']
		exe = prog['exe']
		exeprefix = prog['exeprefix']

		# Let's go to the executable directory
		os.chdir(exedir)
		oraclepath = exedir+'/'+progsuffix[1:]

		if args.usePA:
			oraclepath += '-PA-oracle'
		else:
			oraclepath += '-VA-oracle'

		try:
			print('Making:', oraclepath)
			os.mkdir(oraclepath)
		except OSError as error:
			print('oracle dir may already exist, not creating...')

		# Go into the oracle folder since the create-datasets will dump here
		os.chdir(oraclepath)

		command = debugRun+' python3 '+create_dataset_script+' --agg mean-min --tracedirs'

		for probSize in probSizes:

			inputArgs=prog[probSize]
			suffix = progsuffix+'-'+probSize

			if args.usePA:
				suffix = suffix+'-PA'

			dirname = 'trace-'+suffix[1:]

			command += ' '+exedir+'/'+dirname

		command = 'sbatch -N 1 -n 1 --time="01:00:00" --job-name="'+progsuffix[1:]+'oracle" --output="'+progsuffix[1:]+'-oracle-runlogs.out" --open-mode=append --wrap="'+command+'"'
		print('Going to execute:', command)
		os.system(command)

	print('Static runs launched!')
	return


main()