import os
import time
import subprocess, shlex
import argparse
from benchmarks import *
import importlib
import pandas as pd
from pathlib import Path
from glob import glob
import re
import numpy as np

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from sklearn.gaussian_process.kernels import Matern, DotProduct, RationalQuadratic, RBF
from sklearn.gaussian_process import GaussianProcessRegressor

RANDOM_STATE_SEED = 1783

# This class handles the prepping of job runs, it creates
# all the necessary envvars for each run, it also writes the
# schedules to run to the proper directories for execution.
# The general execution loop is:
# - ask BO for the next point (schedule) to sample
# - do numTrials runs of the benchmark
# - average xtimes of trials -- add as new point in model
class BOJobManager:
	def __init__(self, prog, numTrials, kernelFnct, acqFnct, numPolicies, numRegionExecs, probSize, timeCap):
		self.progname = prog
		self.prog = progs[prog]
		self.numTrials = numTrials
		self.kernel = getattr(importlib.import_module('sklearn.gaussian_process.kernels'), kernelFnct)()
		self.acq_fnct = acqFnct
		self.numPolicies = numPolicies
		self.numRegionExecs = numRegionExecs
		self.probSize = probSize
		self.executedIters = 0
		self.timeCap = timeCap

		# upper bound is exclusive with the bound values
		boundKeys = [ i for i in range(0, numRegionExecs)]
		boundVals = [ (0, numPolicies) for i in range(0, numRegionExecs)]

		# setup the bounds for each dimension
		self.pbounds = dict(zip(boundKeys, boundVals))

		# setup the Bayesian Optimizer
		self.optim = BayesianOptimization(
		    f=None,
		    pbounds=self.pbounds,
				random_state=RANDOM_STATE_SEED
		)

		# utility function = acquisition function
		self.util = UtilityFunction(kind=acqFnct, kappa=10)

		# setup this object with the schedule mapping for this benchmark
		# this gives us the variables regions, regionExecMap, and regionExecMapInv
		self.get_schedule_mapping()
		return

	# Here we'll return a pandas dataframe containing all the data from
	# the csvs that we capture in a directory
	def read_csvs_in_dir(self, csvsDir):

		csvs = list(glob(csvsDir+'/*.csv', recursive=False))
		df = pd.DataFrame()
		for csv in csvs:
			df = pd.concat([df, pd.read_csv(csv, sep=' ')])

		return df

	# This will go through a benchmark's data directory and read a run
	# to learn what order the region executions are in.
	# This is only done at the time of setup for the model
	def get_schedule_mapping(self):
		print('Generating schedule mapping from benchmark data dir')
		exedir = rootdir+self.prog['exedir']
		progsuffix = self.prog['suffix'][1:]

		apollo_data_dir = exedir+'/'+progsuffix+'-data'

		# get the first traces directory within the data directory
		# that matches this problem size. 
		print('reading from:', apollo_data_dir)
		dirs = list(glob(apollo_data_dir+'/*'+self.probSize+'*-traces/', recursive=False))

		# read in the csvs in the first directory
		execDataDF = self.read_csvs_in_dir(dirs[0])

		print(execDataDF.head())
		# let's focus on only particular rows so we can then drop duplicates
		execDataDF = execDataDF[['region', 'globalidx']].drop_duplicates()

		# sort the dataframe by region execution index
		execDataDF = execDataDF.sort_values(by='globalidx', ascending=True)

		assert execDataDF.shape[0] == self.numRegionExecs

		# now make a dictionary of the regions, this will tell us which
		# indices correspond to which regions
		regions = list(execDataDF['region'].unique())

		# save a list of regions of execution
		self.regions = regions

		mapping = {}
		for region in regions:
			mapping[region] = list(execDataDF[execDataDF['region'] == region]['globalidx'])

		print(mapping)
		self.regionExecMap = mapping

		# calculate an inverse mapping to make it easy to map back
		# which region execution index belongs to which region
		self.regionExecMapInv = list(execDataDF['region'])

		return mapping

	def get_region_dict_from_sched_dict(self, raw_sched):
		sched = {region: [] for region in self.regions}

		for idx,policy in raw_sched.items():
			region = self.regionExecMapInv[idx]
			sched[region].append(policy)

		return sched

	# This will write out the desired schedule for a given execution
	def write_schedule(self, raw_sched, targetDir):
		# The raw input schedule is just an ordered list of policies for each region execution
		# We're going to convert it to a dictionary
		sched = self.get_region_dict_from_sched_dict(raw_sched)
		print('floored schedule',sched)

		# for each region, let's write a file with its schedule
		for region in sched:
			filename = targetDir+'/opt-'+region+'-rank-0.txt'

			#make sure the filepath exists
			os.makedirs(os.path.dirname(filename), exist_ok=True)

			# we will overwrite whatever file has this name in the provided dir
			with open(filename, 'w') as towrite:
				strlist = [str(i) for i in sched[region]]
				towrite.write(','.join(strlist))

		return

	def get_next_point_to_sample(self):
		return self.optim.suggest(self.util)

	def update_GP_model(self, x, y):
		self.optim.register( params=x, target=y)
		return

	# unfortunately slurm removes entries from the squeue list
	# after they fully complete, can't really check there for
	# completion. We can use the strigger command to invoke something
	# but it's honestly just easier to go into a job output file
	# and find the keyword "logout". We make all the job output
	# files unique in name, and we keep track of the names, so we
	# can periodically read them. This output file will only contain
	# an xtime number and the keyword "logout" indicating the job 
	# completed. Another big assumption is that there only exists
	# one xtime floating point in the file. This will read all the
	# matches in the file and extract the last one.
	def get_run_xtime(self, outputFilename):
		# check if the file exists

		outfile = Path(outputFilename)

		# if the checkpoint file does not exist
		if outfile.is_file():
			with open(outputFilename, 'r') as toread:
				all_text = toread.read()
				# if the job finished, extract the xtime
				if 'logout' in all_text:
					matches = re.findall(r"[-+]?(?:\d*\.*\d+)", all_text)
					return float(matches[-1])

		return 0.0

	# This will stall us if not all the jobs are completed
	# we want this behavior because for BO we need to wait for
	# the runs to complete anyways.
	# jobs is just an array of output filenames to be read
	def wait_for_jobs_to_complete(self, jobs):
		numJobs = len(jobs)
		jobStatus = [0.0]*numJobs
		# use an indicator variable to check for job completion
		# if all jobs are complete, all indicators are 1 and should
		# sum to the numJobs
		while sum([ int(i != 0.0) for i in jobStatus]) != numJobs:
			for idx,job in enumerate(jobs):
				jobStatus[idx] = self.get_run_xtime(job)

		return jobStatus

	def launch_run(self, envvars, outfileName, timeCap):

		# example run command:
		# export PROGRAM_TO_RUN=./ft.C.x
		# sbatch run_single_benchmark.sh --output=filename --time=h:mm:ss --job-name=test

		jobName = self.progname+'-run'

		outputFile = APOLLO_DATA_COLLECTION_DIR+'/outputfiles/'+outfileName

		command = 'sbatch --output='+outputFile+' --time='+timeCap+' --job-name='+jobName+ ' ./run_single_benchmark.sh'
		print('executing command:', command)
		subprocess.call(shlex.split(command), env=envvars)


		# this output file is a FULL path
		return outputFile

	# this will test one schedule for numTrials amount of times
	def setup_run_with_sched(self, sched):
		# sched is of type dictionary, mapping each region execution index to a policy

		exedir = rootdir+self.prog['exedir']
		progsuffix = self.prog['suffix'][1:]

		exe = self.prog['exe']
		exeprefix = self.prog['exeprefix']
		datapath = self.prog['datapath']
		xtimeline = self.prog['xtimelinesearch']
		xtimescalefactor = float(self.prog['xtimescalefactor'])

		apollo_data_dir = exedir+'/'+progsuffix+'-data'

		# all these are local to the apollo data dir
		apollo_trial_dir = progsuffix+'-'+self.probSize+'-BO_guided-iter='+str(self.executedIters)
		apollo_trace_dir = apollo_trial_dir + '-traces'
		apollo_dataset_dir = apollo_trial_dir + '-datasets'
		apollo_models_dir = apollo_trial_dir + '-models'
	
		envvars['APOLLO_OUTPUT_DIR'] = apollo_data_dir 
		envvars['APOLLO_TRACES_DIR'] = apollo_trace_dir
		envvars['APOLLO_DATASETS_DIR'] = apollo_dataset_dir
		envvars['APOLLO_MODELS_DIR'] = apollo_models_dir
		envvars['APOLLO_OPTIM_READ_DIR'] = progsuffix+'-data/'+apollo_trial_dir
		envvars['APOLLO_POLICY_MODEL']='Optimal'

		# when executing the program, sbatch will cd here
		envvars['EXE_DIR'] = exedir

		# make desired schedule to the execute
		self.write_schedule(sched, apollo_data_dir+'/'+apollo_trial_dir)

		inputArgs=self.prog[self.probSize]

		# String replacement for full paths to input files
		if len(datapath) > 0:
			# count the number of replacements to make
			numtorep = inputArgs.count('%s')
			strtorep = exedir+'/'+datapath
			replTuple = tuple([strtorep]*numtorep)
			inputArgs = inputArgs%replTuple

		command = exeprefix+'./'+str(exe)+str(inputArgs)
		envvars['PROGRAM_TO_RUN'] = command

		vars_to_use = {**os.environ.copy(), **envvars}

		# return the environment variables we're going to run with
		return vars_to_use

	# adds the gathered static data to the checkpoint file
	def gather_static_run_data(self, chkpt):
		keys = [ i for i in range(self.numRegionExecs)]

		# for each policy, build a schedule vector and execute with it
		for policy in range(self.numPolicies):
			vals = [policy]*self.numRegionExecs
			x = dict(zip(keys, vals))

			jobFiles = []

			# we are not doing traced runs
			envvars = self.setup_run_with_sched(x)

			for i in range(self.numTrials):
				outfileName = self.progname+'-'+self.probSize+'-static-pol' + str(policy)+ 'trial'+str(i)+'.txt'
				outfile = self.launch_run(envvars, outfileName, self.timeCap)
				jobFiles.append(outfile)

			xtimes = self.wait_for_jobs_to_complete(jobFiles)
			print('Got xtimes of', xtimes)
		
			y = np.mean(xtimes)
			print('mean xtime of: ', y)

			chkpt.add_new_point(x,y)
			self.update_GP_model(x, -y)

		return

	def iterate(self):
		x = self.get_next_point_to_sample()
		print('on iteration: ', self.executedIters)
		print('testing point: ', x, type(x))

		# need to floor all the values
		for idx,policy in x.items():
			#x[idx] = int(policy)
			x[idx] = round(policy, 0)

		jobFiles = []

		# we are not doing traced runs
		envvars = self.setup_run_with_sched(x)

		for i in range(self.numTrials):
			outfileName = self.progname+'-'+self.probSize+'-iter' + str(self.executedIters)+ 'trial'+str(i)+'.txt'
			outfile = self.launch_run(envvars, outfileName, self.timeCap)
			jobFiles.append(outfile)

		xtimes = self.wait_for_jobs_to_complete(jobFiles)
		print('Got xtimes of', xtimes)
		
		y = np.mean(xtimes)
		print('mean xtime of: ', y)

		# GP can only maximize an objective, since
		# we want to minimize xtime, we need to make
		# the time value negative
		self.update_GP_model(x, -y)
		self.executedIters += 1
		return (x,y)


class CSVCheckpointer:
	def __init__(self, checkpointFilename, numRegionExecs):
		# get the current directory and make the filename a FULL path
		cwd = str(os.getcwd())
		self.checkpointFilename = cwd+'/'+checkpointFilename
		self.numRegionExecs = numRegionExecs

		# check if the checkpoint exists
		chkptFile = Path(self.checkpointFilename)

		# if the checkpoint file does not exist
		if not chkptFile.is_file():
			# create the df with just the header
			self.df = pd.DataFrame(columns = ['xtime']+['f'+str(i) for i in range(self.numRegionExecs)], dtype=float)

			# write the file out
			self.df.to_csv(self.checkpointFilename, index=False)
		else:
			# read in the checkpoint file
			self.df = pd.read_csv(checkpointFilename)
		
		return

	def add_new_point(self, x, y):
		# convert x dictionary into an array
		csvRow = pd.DataFrame([[y]+list(x.values())], dtype=float)

		# add the data to the dataframe
		self.df = pd.concat([self.df, csvRow])

		# append to the checkpoint, better than re-writing the whole file
		csvRow.to_csv(self.checkpointFilename, mode='a', index=False, header=False)
		return

	def get_checkpoint_data(self):
		# return a list of tuples in the form of [(x,y), (x,y), (x,y)]
		# where x is a dictionary and y is an xtime float 
		# this allows us to easily add points to the GP model 

		toReturn = []
		keys = [ i for i in range(self.numRegionExecs)]

		for index, row in self.df.iterrows():
			# go through all the elements in this row
			vals = list(row[1:])
			x = dict(zip(keys, vals))
			y = row[0]
			toReturn.append((x,y))

		return toReturn

	def was_point_already_sampled(self, x):
		csvRow = pd.DataFrame([list(x.values())], dtype=float)
		wasSampled = (self.df[self.df.columns[1:]] == csvRow).all(axis=1).any()
		return wasSampled


def main():
	print('Starting testing!')
	parser = argparse.ArgumentParser(description='Guide tuning of a suite of benchmarks using Bayesian Optimization')
	parser.add_argument('--kernelFnct', help='What scikitlearn kernel to use (with default params)', default='Matern', type=str)
	parser.add_argument('--acqFnct', help='What acquisition function to use (with default params)', default='ucb', type=str)

	parser.add_argument('--prog', help='What benchmark should we test with?', default='nas_ft', type=str)
	parser.add_argument('--probSize', help='What benchmark problem size should we test with?', default='medprob', type=str)

	# numRegionExecs is just a sanity check for when we pull a sample execution schedule
	parser.add_argument('--numRegionExecs', help='Number of region executions of the program', default=111, type=int)
	parser.add_argument('--numPolicies', help='Number of policies to explore', default=24, type=int)
	parser.add_argument('--chkptCSV', help='Name of the CSV file to write checkpoints to', default='savedRuns.csv', type=str)
	parser.add_argument('--doStaticRuns', action='store_true', help='Should be do pre-training static runs?')
	parser.add_argument('--numTrials', help='The number of trials to average for BO', default=3, type=int)

	parser.add_argument('--timeCap', help='How much time to use for each benchmark execution', default='0:02:00', type=str)

	args = parser.parse_args()
	print('Got input args:', args)

	jobman = BOJobManager(args.prog, args.numTrials, args.kernelFnct, 
												args.acqFnct, args.numPolicies, args.numRegionExecs, 
												args.probSize, args.timeCap)

	chkptCSV_name = jobman.progname+'-'+jobman.probSize+'-'+args.chkptCSV
	chkpt = CSVCheckpointer(chkptCSV_name, args.numRegionExecs)

	# get the checkpoint data and add it to the model
	for datapoint in chkpt.get_checkpoint_data():
		print('adding pre-trained point', datapoint)
		x = datapoint[0]
		y = datapoint[1]
		jobman.update_GP_model(x, -y)

	if args.doStaticRuns:
		jobman.gather_static_run_data(chkpt)

	bestxtime = 1000
	bestpolicy = None
	xtimes = []
	xtime = 1000.0
	# stop when we find an xtime that beats out the best static xtime
	while xtime > 10.77:
		policy, xtime = jobman.iterate()
		chkpt.add_new_point(policy, xtime)
		xtimes.append(xtime)
		print('execution times thus far: ', xtimes)
		if xtime < bestxtime:
			print('new best xtime found!', xtime, '\npolicy', policy, '\n', jobman.get_region_dict_from_sched_dict(policy))
			bestxtime = xtime
			bestpolicy = policy

	print('finished iterating')
	print('best xtime and policy', bestxtime, '\npolicy', bestpolicy, '\n', jobman.get_region_dict_from_sched_dict(bestpolicy))

	print('Testing complete!')
	return


if __name__ == "__main__":
	main()