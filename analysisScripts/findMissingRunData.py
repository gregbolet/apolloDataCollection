import os
import subprocess, shlex
import argparse
import sys
import time
import pandas as pd
import re
from pathlib import Path

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from new_benchmarks import *

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']
#policies=['Static,policy=0', 'Static,policy=1']
probSizes=['smallprob', 'medprob', 'largeprob']
prognames = list(progs.keys())

parser = argparse.ArgumentParser(
    description='Launch static runs of benchmark programs using Apollo.')
parser.add_argument('--checkType', help='Should we do a static, online, or oracle check?', default='static',
                    type=str)
parser.add_argument('--numTrials', help='How many trials to run with', default=10,
                    type=int)

args = parser.parse_args()
print('I got args:', args)


# This function will read the CSV file with data
# and then generate a list of trials yet to finish
def get_work_from_checkpoint():
	todo = [(x,y,z,w) for x in prognames for y in probSizes for z in policies for w in range(args.numTrials)]
	#todo.sort()
	print('todo', len(todo))
	df = pd.DataFrame(columns=['progname', 'probSize', 'policy', 'trialnum', 'eteXtime'])

	datafilepath = APOLLO_DATA_COLLECTION_DIR+'/'+args.checkType+'-ETE-XTimeData_VA.csv'

	#if the datafile exists, read from it
	if Path(datafilepath).exists():
		tempdf = pd.read_csv(datafilepath)

		# if we have more than 1 data point, let's remove items
		if tempdf.shape[0] > 0:
			# Based on what's already done, let's remove these elements from the todo list
			for row in tempdf.itertuples(index=False, name=None):
				trial = row[0:4]
				#print('trial we have:', trial)
				if trial in todo:
					todo.remove(trial)

			# return the read-in dataframe
			return (todo, tempdf)

	return (todo, df)


def main():
	print('Starting comparison...')

	vatodo, vadf = get_work_from_checkpoint()
	patodo, padf = get_work_from_checkpoint()

	print('VA TODO:', len(vatodo), 'PA TODO:', len(patodo))

	print('VA TODO:', 'items', vatodo)
	print('PA TODO:', 'items', patodo)

	return

main()