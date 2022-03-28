#!/usr/tce/packages/python/python-3.8.2/bin/python3

import os
import subprocess
import numpy as np
import pandas as pd
import glob

# This program will examine the rundata for the static0, static1, static2
# policies of each target program. Then it will parse the TRACE_CSV files to quantify
# whether there is potential for speedup in each program
# We consider a program to have speedup potential if none of the static policies
# has a time-weighted accuracy of greater than 95%

progs={

			 'rodinia_backprop':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/backprop',
							   'exe':'backprop ',
								 'exeprefix':'',
							   'suffix':'-backprop',
							   'smallprob':'65536 16 1',
							   'medprob':  '65536 65536 2048',
							   'largeprob':'65536 65536 65536'},

			 'rodinia_cfd':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/cfd',
							   'exe':'euler3d_cpu ',
								 'exeprefix':'',
							   'suffix':'-cfd',
							   'smallprob':'../../data/cfd/fvcorr.domn.193K',
							   'medprob':  '../../data/cfd/missile.domn.0.2M',
							   'largeprob':'../../data/cfd/missile.domn.0.4M'},

			 'rodinia_heartwall':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
							   'exe':'heartwall ',
								 'exeprefix':'',
							   'suffix':'-heartwall',
							   'smallprob':'../../data/heartwall/test.avi 20 4',
							   'medprob':  '../../data/heartwall/test.avi 52 4',
							   'largeprob':'../../data/heartwall/test.avi 104 4'},

			 'rodinia_hotspot':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/hotspot',
							   'exe':'hotspot ',
								 'exeprefix':'',
							   'suffix':'-hotspot',
							   'smallprob':'1024 1024 2000 4000 ../../data/hotspot/temp_1024 ../../data/hotspot/power_1024 output.out',
							   'medprob':  '4096 4096 2000 4000 ../../data/hotspot/temp_4096 ../../data/hotspot/power_4096 output.out',
							   'largeprob':'16384 16384 2000 4000 ../../data/hotspot/temp_16384 ../../data/hotspot/power_16384 output.out'},

			 'rodinia_leukocyte':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/leukocyte',
							   'exe':'OpenMP/leukocyte ',
								 'exeprefix':'',
							   'suffix':'-leukocyte',
							   'smallprob':'99 36 ../../data/leukocyte/testfile.avi',
							   'medprob':  '399 36 ../../data/leukocyte/testfile.avi',
							   'largeprob':'599 36 ../../data/leukocyte/testfile.avi'},

			 'rodinia_lud':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/lud',
							   'exe':'omp/lud_omp ',
								 'exeprefix':'',
							   'suffix':'-lud',
							   'smallprob':'-s 4096',
							   'medprob':  '-s 16384',
							   'largeprob':'-s 32768'},

			 'rodinia_nn':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/nn',
							   'exe':'nn ',
								 'exeprefix':'',
							   'suffix':'-nn',
							   'smallprob':'filelist_4 5 30 90',
							   'medprob':  'filelist_160k 5 30 90',
							   'largeprob':'filelist_2560k 5 50 90'},

			 'rodinia_nw':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/nw',
							   'exe':'needle ',
								 'exeprefix':'',
							   'suffix':'-nw',
							   'smallprob':'23000 10 36',
							   'medprob':  '33000 10 36',
							   'largeprob':'46000 10 36'},

			 'rodinia_pathfinder':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/pathfinder',
							   'exe':'pathfinder ',
								 'exeprefix':'',
							   'suffix':'-pathfinder',
							   'smallprob':'25000 25000 > out',
							   'medprob':  '5000 5000 > out',
							   'largeprob':'10000 10000 > out'},

			 'rodinia_sradv1':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/srad/srad_v1',
							   'exe':'srad ',
								 'exeprefix':'',
							   'suffix':'-sradv1',
							   'smallprob':'10 0.5 5002 5002 36',
							   'medprob':  '100 0.5 5002 5002 36',
							   'largeprob':'1000 0.5 5002 5002 36'},

			 #'rodinia_sradv2':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/srad/srad_v2',
				#			   'exe':'srad ',
				#				 'exeprefix':'',
				#			   'suffix':'-sradv2',
				#			   'smallprob':'4096 4096 0 127 0 127 36 0.5 1000',
				#			   'medprob':  '8192 8192 0 127 0 127 36 0.5 1000',
				#			   'largeprob':'8192 8192 0 127 0 127 36 0.5 10000'},

	'comd':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/CoMD/omp',
							'exe':'CoMD-openmp ',
							'exeprefix':'',
							'suffix':'-comd',
							'smallprob':'-e -i 1 -j 1 -k 1 -x 50 -y 50 -z 50',
							'medprob':  '-e -i 1 -j 1 -k 1 -x 100 -y 100 -z 100',
							'largeprob':'-e -i 1 -j 1 -k 1 -x 200 -y 200 -z 200'},

	'minife':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/miniFE/omp',
							'exe':'miniFE.x ',
							'exeprefix':'',
							'suffix':'-minife',
							'smallprob':'-nx 128',
							'medprob':  '-nx 256',
							'largeprob':'-nx 400'},

			 'nas_bt':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-bt'},

			 'nas_cg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-cg'},

			 'nas_ep':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-ep'},

			 'nas_ft':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-ft'},

			 'nas_lu':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-lu'},

			 'nas_sp':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-sp'},

			 'nas_mg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'suffix':'-mg'},

				'amg':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/AMG/omp',
							'suffix':'-amg'},

 				'quicksilver':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/Quicksilver/omp',
								        'suffix':'-qs'},

			 'xsbench':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/XSBench/omp',
							    'suffix':'-xsbench'},

			 'lulesh':{'exedir':'/g/g15/bolet1/workspace/lulesh-region-fix-correct/LULESH/build',
							    'suffix':'-lulesh'},

			 }

staticPols=[0,1,2]
probSizes=['smallprob', 'medprob', 'largeprob']

def main():
	print('Starting analysis...')
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