#!/usr/tce/packages/python/python-3.8.2/bin/python3

import os
import subprocess
import numpy as np
import pandas as pd
import glob
from benchmarks import progs
import argparse

# This program will examine the rundata for the static0, static1, static2
# policies of each target program. Then it will parse the TRACE_CSV files to quantify
# whether there is potential for speedup in each program
# We consider a program to have speedup potential if none of the static policies
# has a time-weighted accuracy of greater than 95%

staticPols=[0,1,2]
probSizes=['smallprob', 'medprob', 'largeprob']

def main():
	print('Starting analysis...')

	parser = argparse.ArgumentParser(
	    description='Launch static runs of benchmark programs using Apollo.')
	parser.add_argument('--usePA', action='store_true',
	                    help='Should we use PA data instead of VA?')
	args = parser.parse_args()

	# For each program
	for progname in progs:
			prog = progs[progname]
			progsuffix = prog['suffix']
			exedir = prog['exedir']

			# Let's go to the executable directory
			os.chdir(exedir)
			print()

			# For each problem size, let's load in the data
			for probSize in probSizes:

				foldername = 'trace'+progsuffix+'-'+probSize

				if args.usePA:
					foldername += '-PA'

				# Go into the problem-size folder
				os.chdir(exedir+'/'+foldername)
				print(os.getcwd())
				csvs = list(glob.glob("*.csv"))

				staticPols = [0, 1, 2]

				#print('Reading in all CSV files for', foldername)
				df = pd.DataFrame()
				# Let's load up each CSV into one big df
				for csv in csvs:
					# ignore the feature columns since they may have diff counts
					#print('reading csv:', csv)
					try:
						rawdf = pd.read_csv(csv, sep=' ', usecols=['region', 'idx', 'policy', 'xtime'])
						#print(csv, ' ', end='')
						#print(rawdf.dtypes)
						#rawdf = pd.read_csv(csv, sep=' ', header=0)

						df = df.append(rawdf)
					except pd.errors.EmptyDataError:
						# if we fail to read a csv, that means the program timed out on a certain policy
						polLoc = csv.find('policy=')
						policy = int(csv[polLoc+7:csv.find('-',polLoc)])

						if policy in staticPols:
							staticPols.remove(policy)

				#print('CSV reading complete')
				# After we've read in all the csvs, let's do some sanity checks
				# the static0, static1, and static2 measurements should all have the same counts
				for staticPol in staticPols:
					print( df.loc[df['policy'] == staticPol].shape[0], end=' ')
					for staticPol2 in staticPols:
						if staticPol != staticPol2:
							assert( df.loc[df['policy'] == staticPol].shape[0] == df.loc[df['policy'] == staticPol2].shape[0] )

				print()
				#print('Sanity check assertion complete')
				#print(df.head())

				# Let's create the oracle dataset, indexed by idx and region
				opt = df.sort_values(by=['xtime']).drop_duplicates(['region', 'idx'], keep='first').set_index(['region', 'idx']).sort_index()


				# Add the percent-xtime column to the optimal
				optsum = opt['xtime'].sum()
				opt['pxtime'] = opt['xtime']/optsum

				#print('Optimal oracle policy generated')

				# Let's go through each static policy and check its accuracy
				for staticPol in staticPols:
					#print('Checking time-weighted accuracy of policy:', staticPol)
					staticdf = df.loc[df['policy'] == staticPol].set_index(['region', 'idx']).sort_index()

					# True/False indicators of policy match
					polMatches = staticdf[['policy']].isin(opt[['policy']])
					#print(polMatches)

					numRegionExecutions = len(polMatches.index)

					# Get the matches and calculate the accuracies
					matches = polMatches.loc[polMatches['policy'] == True]
					numMatches = int(matches.count())
					rawAcc = (100.0*numMatches)/numRegionExecutions

					# The weighted accuracy is a better metric than the raw accuracy.
					# This is because a program may have 99% raw accuracy, but if that 1%
					# takes up 80% of the xtime, then our true accuracy is only 20%
					# because we didn't properly predict for the executions that mattered
					# the most.
					weightedAcc = opt.loc[matches.index]['pxtime'].sum()*100.0

					print('%s: policy %d | Raw Accuracy: %.4f %% (time-weighted: %.4f %%)'%(foldername, staticPol, rawAcc, weightedAcc))
					print('Static xtime: %.4f secs (optimal: %.4f secs)'%(staticdf['xtime'].sum(), opt['xtime'].sum()))

	print('Analysis Complete!')
	return

main()