import os
import time
import subprocess, shlex
import argparse
from benchmarks import *
import importlib
import pandas as pd
from pathlib import Path
from glob import glob

from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from sklearn.gaussian_process.kernels import Matern, DotProduct, RationalQuadratic, RBF
from sklearn.gaussian_process import GaussianProcessRegressor

RANDOM_STATE_SEED = 1783

class GPModel:
	def __init__(self, prog, probSize, kernel, acqFnct, priorSamples, iters, numPolicies, numRegionExecs):
		self.progname = prog
		self.prog = progs[prog]
		self.kernel = getattr(importlib.import_module('sklearn.gaussian_process.kernels'), kernel)()
		self.acq_fnct = acqFnct
		self.numPolicies = numPolicies
		self.numRegionExecs = numRegionExecs
		self.probSize = probSize
		self.iters = iters
		self.executedIters = 0

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
		self.util = UtilityFunction(kind=acqFnct, kappa=2.5, xi=0.0)

		# setup this object with the schedule mapping for this benchmark
		# this gives us the variables regions, regionExecMap, and regionExecMapInv
		self.get_schedule_mapping()
		return
	
	def __str__(self):
		return 'kernel = ' + str(self.kernel) + '\n' + \
					 'acquisition fnct = ' + str(self.util.kind) + '\n' + \
					 'bounds = ' + str(self.pbounds)

	# raw_sched is a dictionary
	def get_sched_dict_from_list(self, raw_sched):
		sched = {region: [] for region in self.regions}

		for idx,policy in raw_sched.items():
			region = self.regionExecMapInv[idx]
			sched[region].append(policy)

		return sched

	# This will write out the desired schedule for a given execution
	def write_schedule(self, raw_sched, targetDir):
		# The raw input schedule is just an ordered list of policies for each region execution
		# We're going to convert it to a dictionary
		sched = self.get_sched_dict_from_list(raw_sched)
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

		# get the first directory within the data directory
		print('reading from:', apollo_data_dir)
		dirs = list(glob(apollo_data_dir+'/*/', recursive=False))

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

	# This will go through the CSV trace files of a certain dir and
	# return the schedule it executed under
	# This will be implemented later when we want to load up old data
	# that has already been recorded
	def read_schedule(self, targetDir):
		sched = {}
		# get the first directory within the data dir

		# go into the ft-data directory and 
		return sched

	def get_next_point_to_sample(self):
		return self.optim.suggest(self.util)

	def update_GP_model(self, x, y):
		self.optim.register( params=x, target=y)
		return

	def get_total_xtimes_from_csvs(self, dir):

		return

	# we assume that sched is just a vector of policies for each region execution
	def run_prog_with_sched(self, sched):

		exedir = rootdir+self.prog['exedir']
		progsuffix = self.prog['suffix'][1:]

		exe = self.prog['exe']
		exeprefix = self.prog['exeprefix']
		datapath = self.prog['datapath']
		xtimeline = self.prog['xtimelinesearch']
		xtimescalefactor = float(self.prog['xtimescalefactor'])

		apollo_data_dir = exedir+'/'+progsuffix+'-data'
		#apollo_trial_dir = apollo_data_dir+'/'+progsuffix+'-'+self.probSize+'-BO_guided-iter='+str(self.executedIters)
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

		# Let's go to the executable directory
		os.chdir(exedir)

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

		vars_to_use = {**os.environ.copy(), **envvars}

		command = exeprefix+'./'+str(exe)+str(inputArgs)

		# start a log file to print the outputs of the trial
		mystdoutpath = apollo_data_dir+'/'+apollo_trial_dir+'/'+'logfile.txt'
		print('writing to log file:', mystdoutpath)
		mystdout = open(mystdoutpath, 'a')
		
		mystdout.write('using envvars:\n' + str(envvars) + '\n')
		mystdout.write('Going to execute:'+str(command)+'\n')
		# Get the end-to-end xtime
		#ete_xtime = time.time()
		ete_xtime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
		subprocess.call(shlex.split(command), env=vars_to_use, stdout=mystdout, stderr=mystdout)
		ete_xtime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - ete_xtime

		mystdout.flush()

		self.executedIters += 1

		# now let's see if we can get the xtime from the stdout
		if xtimeline != '':
			file_xtime = get_file_last_line_timing_match(mystdoutpath, xtimeline)
			if file_xtime != None:
				return file_xtime*xtimescalefactor

		return ete_xtime*xtimescalefactor


	def iterate(self):
		x = self.get_next_point_to_sample()
		print('on iteration: ', self.executedIters)
		print('testing point: ', x, type(x))

		# need to floor all the values
		for idx,policy in x.items():
			x[idx] = int(policy)

		y = self.run_prog_with_sched(x)
		print('got xtime of: ', y)

		# GP can only maximize an objective, since
		# we want to minimize xtime, we need to make
		# the time value negative
		self.update_GP_model(x, -y)
		return (x,y)

def parse_input_args():
	parser = argparse.ArgumentParser(description='Guide tuning of the FT benchmark using Bayesian Optimization')
	parser.add_argument('--kernel', help='What scikitlearn kernel to use (with default params)', default='Matern', type=str)
	parser.add_argument('--acqFnct', help='What acquisition function to use (with default params)', default='ucb', type=str)

	# iters and priorSamples go unused for now
	parser.add_argument('--priorSamples', help='Number of points to sample before guiding tuning', default=0, type=int)
	parser.add_argument('--iters', help='Number of iterations to take of guided tuning', default=3, type=int)

	parser.add_argument('--prog', help='What benchmark should we test with?', default='nas_ft', type=str)
	parser.add_argument('--probSize', help='What benchmark problem size should we test with?', default='medprob', type=str)

	# numRegionExecs is just a sanity check for when we pull a sample execution schedule
	parser.add_argument('--numRegionExecs', help='Number of region executions of the program', default=111, type=int)
	parser.add_argument('--numPolicies', help='Number of policies to explore', default=24, type=int)

	args = parser.parse_args()
	print('I got args:', args)
	return args

def main():
	args = parse_input_args()
	model = GPModel(args.prog, args.probSize, args.kernel, args.acqFnct, args.priorSamples, 
									 args.iters, args.numPolicies, args.numRegionExecs)

	bestxtime = 1000
	bestpolicy = None
	xtimes = []
	xtime = 1000.0
	while xtime > 10.0:
		policy, xtime = model.iterate()
		xtimes.append(xtime)
		print('execution times thus far: ', xtimes)
		if xtime < bestxtime:
			print('new best xtime found!', xtime, '\npolicy', policy, '\n', model.get_sched_dict_from_list(policy))
			bestxtime = xtime
			bestpolicy = policy

	print('finished iterating')
	print('best xtime and policy', bestxtime, '\npolicy', bestpolicy, '\n', model.get_sched_dict_from_list(bestpolicy))
	return

if __name__ == "__main__":
	main()
