import os
import re

APOLLO_DATA_COLLECTION_DIR='/g/g15/bolet1/workspace/apolloDataCollection/slurmBayesianOptim'

rootdirs={
	'quartz': '/g/g15/bolet1/workspace/',
	'ruby': '/g/g15/bolet1/workspace/ruby/',
	'lassen': '/g/g15/bolet1/workspace/lassen/'
}

# This script assumes that you have logged-in to the target machine
# and have run 'source ~/.profile' to setup the envvars for the
# proper compiler. Then you can run this script.

hostname = os.uname()[1]
rootdir = ''
if 'quartz' in hostname:
	hostname='quartz'
elif 'ruby' in hostname:
	hostname='ruby'
else:
	hostname='lassen'
	hostname='quartz'

rootdir = rootdirs[hostname]

# These are the default number of trials we want to run for each configuration
NUM_TRIALS = 5
#NUM_TRIALS = 4

# These are the tags used by the MPI communicators
ROOT_RANK = 0
REQUEST_WORK_TAG = 11
ACK_WORK_TAG = 12
DONE_WORK_TAG = 13
NEW_WORK_TAG = 14

# Set the default env vars
envvars={
	'OMP_WAIT_POLICY':"active",
	'OMP_PROC_BIND':"close",
	'OMP_PLACES':"cores",
	'APOLLO_COLLECTIVE_TRAINING':'0' ,
	'APOLLO_LOCAL_TRAINING':'1' ,
	'APOLLO_RETRAIN_ENABLE':'0' ,
	'APOLLO_STORE_MODELS':'0',
	'APOLLO_TRACE_CSV':'0',
	'APOLLO_SINGLE_MODEL':'0' ,
	'APOLLO_REGION_MODEL':'1' ,
	'APOLLO_GLOBAL_TRAIN_PERIOD':'0',
	'APOLLO_ENABLE_PERF_CNTRS':'0' ,
	'APOLLO_PERF_CNTRS_SAMPLE_EACH_ITER':'0',
	'APOLLO_PERF_CNTRS_MLTPX':'0' ,
	'APOLLO_PERF_CNTRS':"PAPI_DP_OPS" ,
	'APOLLO_MIN_TRAINING_DATA':"0",
	'APOLLO_PERSISTENT_DATASETS':"0",
	'APOLLO_OUTPUT_DIR':"my-test",
	'APOLLO_DATASETS_DIR':"my-datasets",
	'APOLLO_TRACES_DIR':"my-traces",
	'APOLLO_MODELS_DIR':"my-models",
	'APOLLO_OPTIM_READ_DIR':"./",
}

#depending on the hostname, lets set the thread count
# lassen is the default
if hostname == 'quartz':
	envvars['OMP_NUM_THREADS'] = '36'
elif hostname == 'ruby':
	envvars['OMP_NUM_THREADS'] = '56'
else:
	envvars['OMP_NUM_THREADS'] = '40'

# open and go through a file to get the last occurence of line
# with a particular substring. We then search this line for 
# a floating point xtime value and return that
def get_file_last_line_timing_match(filename, line_substring):

	lines = []
	with open(filename, 'r') as toread:
		for line in toread:
			if line_substring in line:
				lines.append(line)

	if len(lines) > 0:
		# now get the last line
		last_line = lines[len(lines)-1]
		floats = re.findall(r"[-|+]?\d*\.?\d*[e|E]?[+|-]?\d+", last_line)

		# if we have a nonzero count of floats
		# grab the first one and use that as the timing value
		if len(floats) > 0:
			return float(floats[0])

	return None

# Here we define the programs we will be benchmarking with
# all the directories are mirrored and assumed to be the same
# for each of the root directories
progs={
			 'nas_bt':{
				  'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
					'exe':'',
					'exeprefix':'',
					'suffix':'-bt',
					'datapath':'',
					'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
					'buildcmd':'make bt CLASS=B && make bt CLASS=C && make bt CLASS=D',
					'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
					'cleancmd':'make veryclean',
					'xtimelinesearch':'Time in seconds =',
					'xtimescalefactor': 1,
					'maxruntime':'01:00:00',
					'smallprob':'bt.B.x',
					'medprob':  'bt.C.x',
					'largeprob':'bt.D.x'
				},

			 'nas_cg':{
				 'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
				 'exe':'',
				 'exeprefix':'',
				 'suffix':'-cg',
				 'datapath':'',
				 'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'buildcmd':'make cg CLASS=B && make cg CLASS=C && make cg CLASS=D',
				 'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'cleancmd':'make veryclean',
				 'xtimelinesearch':'Time in seconds =',
				 'xtimescalefactor': 1,
				 'maxruntime':'01:00:00',
				 'smallprob':'cg.B.x',
				 'medprob':  'cg.C.x',
				 'largeprob':'cg.D.x'
				},

			 'nas_ep':{
				 'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
				 'exe':'',
				 'exeprefix':'',
				 'suffix':'-ep',
				 'datapath':'',
				 'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'buildcmd':'make ep CLASS=B && make ep CLASS=C && make ep CLASS=D',
				 'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'cleancmd':'make veryclean',
				 'xtimelinesearch':'Time in seconds =',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:10:00',
				 'smallprob':'ep.B.x',
				 'medprob':  'ep.C.x',
				 'largeprob':'ep.D.x'
				},

			 'nas_ft':{
				 'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
				 'exe':'',
				 'exeprefix':'',
				 'suffix':'-ft',
				 'datapath':'',
				 'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'buildcmd':'make ft CLASS=B && make ft CLASS=C && make ft CLASS=D',
				 'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'cleancmd':'make veryclean',
				 'xtimelinesearch':'Time in seconds =',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:10:00',
				 'smallprob':'ft.B.x',
				 'medprob':  'ft.C.x',
				 'largeprob':'ft.D.x'
				},

			 'nas_lu':{
				 'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
				 'exe':'',
				 'exeprefix':'',
				 'suffix':'-lu',
				 'datapath':'',
				 'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'buildcmd':'make lu CLASS=B && make lu CLASS=C && make lu CLASS=D',
				 'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'cleancmd':'make veryclean',
				 'xtimelinesearch':'Time in seconds =',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:50:00',
				 'smallprob':'lu.B.x',
				 'medprob':  'lu.C.x',
				 'largeprob':'lu.D.x'
				},

			 'nas_sp':{
				 'exedir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
				 'exe':'',
				 'exeprefix':'',
				 'suffix':'-sp',
				 'datapath':'',
				 'builddir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'buildcmd':'make sp CLASS=B && make sp CLASS=C && make sp CLASS=D',
				 'cleandir':'benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C',
				 'cleancmd':'make veryclean',
				 'xtimelinesearch':'Time in seconds =',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:50:00',
				 'smallprob':'sp.B.x',
				 'medprob':  'sp.C.x',
				 'largeprob':'sp.D.x'
				},

			 'rodinia_cfd':{
				 'exedir':'benchmarks/rodinia/rodinia_3.1/openmp/cfd',
				 'exe':'euler3d_cpu ',
				 'exeprefix':'',
				 'suffix':'-cfd',
				 'datapath':'',
				 'builddir':'benchmarks/rodinia/rodinia_3.1/openmp/cfd',
				 'buildcmd':'make euler3d_cpu',
				 'cleandir':'benchmarks/rodinia/rodinia_3.1/openmp/cfd',
				 'cleancmd':'make clean',
				 'xtimelinesearch':'Compute time:',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:15:00',
				 'smallprob':'../../data/cfd/fvcorr.domn.193K',
				 'medprob':  '../../data/cfd/missile.domn.0.2M',
				 'largeprob':'../../data/cfd/missile.domn.0.4M'
				},

			 'rodinia_heartwall':{
				 'exedir':'benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
				 'exe':'heartwall ',
				 'exeprefix':'',
				 'suffix':'-heartwall',
				 'datapath':'../../data/heartwall',
				 'builddir':'benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
				 'buildcmd':'make heartwall',
				 'cleandir':'benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
				 'cleancmd':'make clean',
				 'xtimelinesearch':'',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:10:00',
				 'smallprob':'%s/test.avi 20 36',
				 'medprob':  '%s/test.avi 52 36',
				 'largeprob':'%s/test.avi 104 36'
				},

			 #'rodinia_leukocyte':{
				# 'exedir':'benchmarks/rodinia/rodinia_3.1/openmp/leukocyte',
			 #  'exe':'OpenMP/leukocyte ',
			 #  'exeprefix':'',
			 #  'suffix':'-leukocyte',
			 #  'datapath':'../../data/leukocyte',
			 #  'builddir':'benchmarks/rodinia/rodinia_3.1/openmp/leukocyte',
			 #  'buildcmd':'make OpenMP/leukocyte',
			 #  'cleandir':'benchmarks/rodinia/rodinia_3.1/openmp/leukocyte',
			 #  'cleancmd':'make clean',
			 #  'xtimelinesearch':'Total application run time:',
			 #  'xtimescalefactor': 1,
			 #  'maxruntime':'00:35:00',
			 #  'smallprob':'99 36 %s/testfile.avi',
			 #  'medprob':  '399 36 %s/testfile.avi',
			 #  'largeprob':'599 36 %s/testfile.avi'
				#},

			 'rodinia_lud':{
				 'exedir':'benchmarks/rodinia/rodinia_3.1/openmp/lud',
				 'exe':'omp/lud_omp ',
				 'exeprefix':'',
				 'suffix':'-lud',
				 'datapath':'',
				 'builddir':'benchmarks/rodinia/rodinia_3.1/openmp/lud',
				 'buildcmd':'make lud_omp',
				 'cleandir':'benchmarks/rodinia/rodinia_3.1/openmp/lud',
				 'cleancmd':'make clean',
				 'xtimelinesearch':'Time consumed(ms)',
				 'xtimescalefactor': 1e-3,
				 'maxruntime':'00:45:00',
				 'smallprob':'-s 4096',
				 'medprob':  '-s 16384',
				 'largeprob':'-s 32768'
				},

				# Need to copy the ./pots/* data files into the comd-VA-oracle and comd-PA-oracle folders
	 			'comd':{
	 				'exedir':'faros/FAROS/bin/CoMD/omp',
	 				'exe':'CoMD-openmp ',
	 				'exeprefix':'',
	 				'suffix':'-comd',
	 				'datapath':'',
	 				'builddir':'faros/FAROS',
	 				'buildcmd':'./harness.py -i apolloConfig.yaml -b -p CoMD',
	 				'cleandir':'faros/FAROS',
	 				'cleancmd':'rm -rf ./bin/CoMD',
	 				'xtimelinesearch':'',
	 				'xtimescalefactor': 1,
	 				'maxruntime':'00:30:00',
	 				'smallprob':'-e -i 1 -j 1 -k 1 -x 50 -y 50 -z 50',
	 				'medprob':  '-e -i 1 -j 1 -k 1 -x 100 -y 100 -z 100',
	 				'largeprob':'-e -i 1 -j 1 -k 1 -x 200 -y 200 -z 200'
	 		 	 },

				'minife':{
					'exedir':'faros/FAROS/bin/miniFE/omp',
					'exe':'miniFE.x ',
					'exeprefix':'',
					'suffix':'-minife',
					'datapath':'',
					'builddir':'faros/FAROS',
					'buildcmd':'./harness.py -i apolloConfig.yaml -b -p miniFE',
					'cleandir':'faros/FAROS',
					'cleancmd':'rm -rf ./bin/miniFE',
					'xtimelinesearch':'',
					'xtimescalefactor': 1,
					'maxruntime':'00:20:00',
					'smallprob':'-nx 128',
					'medprob':  '-nx 256',
					'largeprob':'-nx 400'
				 },

			 'quicksilver':{
				 'exedir':'faros/FAROS/bin/Quicksilver/omp',
				 'exe':'qs ',
				 'exeprefix':'',
				 'suffix':'-qs',
				 'datapath':'',
				 'builddir':'faros/FAROS',
				 'buildcmd':'./harness.py -i apolloConfig.yaml -b -p Quicksilver',
				 'cleandir':'faros/FAROS',
				 'cleancmd':'rm -rf ./bin/Quicksilver',
				 'xtimelinesearch':'',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:15:00',
				 'smallprob':'--nSteps 60',
				 'medprob':  '--nSteps 120',
				 'largeprob':'--nSteps 240'
				},

			 'xsbench':{
				 'exedir':'faros/FAROS/bin/XSBench/omp',
				 'exe':'XSBench ',
				 'exeprefix':'',
				 'suffix':'-xsbench',
				 'datapath':'',
				 'builddir':'faros/FAROS',
				 'buildcmd':'./harness.py -i apolloConfig.yaml -b -p XSBench',
				 'cleandir':'faros/FAROS',
				 'cleancmd':'rm -rf ./bin/XSBench',
				 'xtimelinesearch':'Runtime:',
				 'xtimescalefactor': 1,
				 'maxruntime':'00:10:00',
				 'smallprob':'-m event -t 36 -k 1 -s small',
				 'medprob':  '-m event -t 36 -k 1 -s large',
				 'largeprob':'-m event -t 36 -k 1 -s XL'
				},

			 'lulesh':{
				 'exedir':'lulesh-region-fix-correct/LULESH/build',
				 'exe':'lulesh2.0 ',
				 'exeprefix':'',
				 'suffix':'-lulesh',
				 'datapath':'',
				 'builddir':'lulesh-region-fix-correct/LULESH/build',
				 'buildcmd':'make',
				 'cleandir':'lulesh-region-fix-correct/LULESH/build',
				 'cleancmd':'make clean',
				 'xtimelinesearch':'Elapsed time',
				 'xtimescalefactor': 1,
				 'maxruntime':'01:00:00',
				 'smallprob':'-s 30 -r 100 -b 0 -c 8 -i 1000',
				 'medprob':  '-s 55 -r 100 -b 0 -c 8 -i 1000',
				 'largeprob':'-s 80 -r 100 -b 0 -c 8 -i 1000'
				},

}