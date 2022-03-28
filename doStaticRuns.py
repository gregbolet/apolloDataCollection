#!/usr/tce/packages/python/python-3.8.2/bin/python3

import os
import subprocess

# This program will run each of the benchmarks in the static0, static1, static2
# policies. This will allow us to then parse the TRACE_CSV files to quantify
# whether there is potential for speedup by adjusting thread counts

progs={
#			 'nas_bt':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-bt',
#							   'smallprob':'bt.B.x',
#							   'medprob':  'bt.C.x',
#							   'largeprob':'bt.D.x'},
#
#			 'nas_cg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-cg',
#							   'smallprob':'cg.B.x',
#							   'medprob':  'cg.C.x',
#							   'largeprob':'cg.D.x'},
#
#			 'nas_ep':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-ep',
#							   'smallprob':'ep.B.x',
#							   'medprob':  'ep.C.x',
#							   'largeprob':'ep.D.x'},
#
#			 'nas_ft':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-ft',
#							   'smallprob':'ft.B.x',
#							   'medprob':  'ft.C.x',
#							   'largeprob':'ft.D.x'},
#
#			 'nas_lu':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-lu',
#							   'smallprob':'lu.B.x',
#							   'medprob':  'lu.C.x',
#							   'largeprob':'lu.D.x'},
#
#			 'nas_sp':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-sp',
#							   'smallprob':'sp.B.x',
#							   'medprob':  'sp.C.x',
#							   'largeprob':'sp.D.x'},
#
#			 'nas_mg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
#							   'exe':'',
#								 'exeprefix':'',
#							   'suffix':'-mg',
#							   'smallprob':'mg.B.x',
#							   'medprob':  'mg.C.x',
#							   'largeprob':'mg.D.x'},

#			 'rodinia_backprop':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/backprop',
#							   'exe':'backprop ',
#								 'exeprefix':'',
#							   'suffix':'-backprop',
#							   'smallprob':'65536 16 1',
#							   'medprob':  '65536 65536 2048',
#							   'largeprob':'65536 65536 65536'},
#
#			 'rodinia_cfd':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/cfd',
#							   'exe':'euler3d_cpu ',
#								 'exeprefix':'',
#							   'suffix':'-cfd',
#							   'smallprob':'../../data/cfd/fvcorr.domn.193K',
#							   'medprob':  '../../data/cfd/missile.domn.0.2M',
#							   'largeprob':'../../data/cfd/missile.domn.0.4M'},
#
#			 'rodinia_heartwall':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
#							   'exe':'heartwall ',
#								 'exeprefix':'',
#							   'suffix':'-heartwall',
#							   'smallprob':'../../data/heartwall/test.avi 20 4',
#							   'medprob':  '../../data/heartwall/test.avi 52 4',
#							   'largeprob':'../../data/heartwall/test.avi 104 4'},
#
#			 'rodinia_hotspot':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/hotspot',
#							   'exe':'hotspot ',
#								 'exeprefix':'',
#							   'suffix':'-hotspot',
#							   'smallprob':'1024 1024 2000 4000 ../../data/hotspot/temp_1024 ../../data/hotspot/power_1024 output.out',
#							   'medprob':  '4096 4096 2000 4000 ../../data/hotspot/temp_4096 ../../data/hotspot/power_4096 output.out',
#							   'largeprob':'16384 16384 2000 4000 ../../data/hotspot/temp_16384 ../../data/hotspot/power_16384 output.out'},
#
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

			 'rodinia_sradv2':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/srad/srad_v2',
							   'exe':'srad ',
								 'exeprefix':'',
							   'suffix':'-sradv2',
							   'smallprob':'4096 4096 0 127 0 127 36 0.5 1000',
							   'medprob':  '8192 8192 0 127 0 127 36 0.5 1000',
							   'largeprob':'8192 8192 0 127 0 127 36 0.5 10000'},

	#'comd':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/CoMD/omp',
	#						'exe':'CoMD-openmp ',
	#						'exeprefix':'',
	#						'suffix':'-comd',
	#						'smallprob':'-e -i 1 -j 1 -k 1 -x 50 -y 50 -z 50',
	#						'medprob':  '-e -i 1 -j 1 -k 1 -x 100 -y 100 -z 100',
	#						'largeprob':'-e -i 1 -j 1 -k 1 -x 200 -y 200 -z 200'},

	#'minife':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/miniFE/omp',
	#						'exe':'miniFE.x ',
	#						'exeprefix':'',
	#						'suffix':'-minife',
	#						'smallprob':'-nx 128',
	#						'medprob':  '-nx 256',
	#						'largeprob':'-nx 400'},

# SimpleMOC was modified to have 10 iterations (num_iters=10)
# This makes all the runs like 130s long...
#	'simpleMOC':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/SimpleMOC/omp',
#							'exe':'SimpleMOC ',
#							'exeprefix':'',
#							'suffix':'-simplemoc',
#							'smallprob':'-s -t 9',
#							'medprob':  '-s -t 18',
#							'largeprob':'-s -t 36'},



			 #'rodinia_':{'exedir':'',
				#			   'exe':' ',
				#				 'exeprefix':'',
				#			   'suffix':'-',
				#			   'smallprob':'',
				#			   'medprob':  '',
				#			   'largeprob':''},

	#'amg':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/AMG/omp',
	#						'exe':'amg ',
	#						'exeprefix':'mpirun -n 1',
	#						'suffix':'-amg',
	#						'smallprob':'-problem 1 -n 128 128 128',
	#						'medprob':  '-problem 1 -n 256 256 256',
	#						'largeprob':'-problem 1 -n 400 400 400'},

	#		 'quicksilver':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/Quicksilver/omp',
	#						        'exe':'qs ',
	#										'exeprefix':'',
	#						        'suffix':'-qs',
	#						        'smallprob':'--nSteps 60',
	#						        'medprob':  '--nSteps 120',
	#						        'largeprob':'--nSteps 240'},

		#	 'xsbench':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/XSBench/omp',
		#					    'exe':'XSBench ',
		#							'exeprefix':'',
		#					    'suffix':'-xsbench',
		#					    'smallprob':'-t 36 -k 1 -s large -l 10 -p 50000 -m event',
		#					    'medprob':  '-t 36 -k 1 -s large -l 100 -p 500000 -m event',
		#					    'largeprob':'-t 36 -k 1 -s large -l 1000 -p 5000000 -m event'},

		#	 'lulesh':{'exedir':'/g/g15/bolet1/workspace/lulesh-region-fix-correct/LULESH/build',
		#					    'exe':'lulesh2.0 ',
		#							'exeprefix':'',
		#					    'suffix':'-lulesh',
		#					    'smallprob':'-s 30 -r 100 -b 0 -c 8 -i 1000',
		#					    'medprob':  '-s 55 -r 100 -b 0 -c 8 -i 1000',
		#					    'largeprob':'-s 80 -r 100 -b 0 -c 8 -i 1000'}
			 }

policies=['Static,policy=0', 'Static,policy=1', 'Static,policy=2']

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

envvarsList = [var+'='+str(envvars[var]) for var in envvars]
envvarsStr = " ".join(envvarsList)

#debugRun='srun --partition=pdebug -n1 -N1 --export=ALL '
debugRun='srun -n1 -N1 --export=ALL '
probSizes=['smallprob', 'medprob', 'largeprob']

def main():
	print('Starting tests...')

	print('Setting default envvars')
	#[os.environ.setdefault(var, envvars[var]) for var in envvars]
	print('Default environemnt vars set')

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

		for probSize in probSizes:

			inputArgs=prog[probSize]
			suffix = progsuffix+'-'+probSize

			# Let's run all the policies on this problem size
			for policy in policies:

				name = suffix[1:]
				#os.environ.update({'APOLLO_POLICY_MODEL': policy})
				command = envvarsStr+' APOLLO_TRACE_CSV_FOLDER_SUFFIX='+suffix+' APOLLO_POLICY_MODEL='+policy
				#command = command+' '+debugRun+' '+exeprefix+' ./'+exe+inputArgs
				command = command+' '+debugRun+' ./'+exe+inputArgs

				#command = 'sbatch -N 1 -n 1 --time="00:20:00" --output="'+suffix[1:]+'-runlogs.out" --open-mode=append --partition=pdebug --wrap="'+command+'"'
				command = 'sbatch -N 1 -n 1 --time="03:00:00" --job-name="'+name+'" --output="'+name+'-runlogs.out" --open-mode=append --wrap="'+command+'"'

				print('Going to execute:', command)

				#res=subprocess.run([command])
				os.system(command)

	print('Static runs launched!')
	return


main()