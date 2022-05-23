# Here we define the programs we will be benchmarking with
progs={
			 'nas_bt':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-bt',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'01:00:00',
							   'smallprob':'bt.B.x',
							   'medprob':  'bt.C.x',
							   'largeprob':'bt.D.x'},

			 'nas_cg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-cg',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'01:00:00',
							   'smallprob':'cg.B.x',
							   'medprob':  'cg.C.x',
							   'largeprob':'cg.D.x'},

			 'nas_ep':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-ep',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'00:10:00',
							   'smallprob':'ep.B.x',
							   'medprob':  'ep.C.x',
							   'largeprob':'ep.D.x'},

			 'nas_ft':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-ft',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'00:10:00',
							   'smallprob':'ft.B.x',
							   'medprob':  'ft.C.x',
							   'largeprob':'ft.D.x'},

			 'nas_lu':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-lu',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'00:50:00',
							   'smallprob':'lu.B.x',
							   'medprob':  'lu.C.x',
							   'largeprob':'lu.D.x'},

			 'nas_sp':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-sp',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'00:50:00',
							   'smallprob':'sp.B.x',
							   'medprob':  'sp.C.x',
							   'largeprob':'sp.D.x'},

			 'nas_mg':{'exedir':'/g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin',
							   'exe':'',
								 'exeprefix':'',
							   'suffix':'-mg',
								 'datapath':'',
								 'xtimelinesearch':'Time in seconds =',
								 'maxruntime':'00:30:00',
							   'smallprob':'mg.B.x',
							   'medprob':  'mg.C.x',
							   'largeprob':'mg.D.x'},

			 'rodinia_backprop':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/backprop',
							   'exe':'backprop ',
								 'exeprefix':'',
							   'suffix':'-backprop',
								 'datapath':'',
								 'xtimelinesearch':'',
								 'maxruntime':'00:20:00',
							   'smallprob':'65536 16 1',
							   'medprob':  '65536 65536 2048',
							   'largeprob':'65536 65536 65536'},

			 'rodinia_cfd':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/cfd',
							   'exe':'euler3d_cpu ',
								 'exeprefix':'',
							   'suffix':'-cfd',
								 'datapath':'',
								 'xtimelinesearch':'Compute time:',
								 'maxruntime':'00:15:00',
							   'smallprob':'../../data/cfd/fvcorr.domn.193K',
							   'medprob':  '../../data/cfd/missile.domn.0.2M',
							   'largeprob':'../../data/cfd/missile.domn.0.4M'},

			 'rodinia_heartwall':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/heartwall',
							   'exe':'heartwall ',
								 'exeprefix':'',
							   'suffix':'-heartwall',
								 'datapath':'../../data/heartwall',
								 'xtimelinesearch':'',
								 'maxruntime':'00:05:00',
							   'smallprob':'%s/test.avi 20 4',
							   'medprob':  '%s/test.avi 52 4',
							   'largeprob':'%s/test.avi 104 4'},

			 'rodinia_hotspot':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/hotspot',
							   'exe':'hotspot ',
								 'exeprefix':'',
							   'suffix':'-hotspot',
								 'datapath':'../../data/hotspot',
								 'xtimelinesearch':'Total time:',
								 'maxruntime':'00:45:00',
							   'smallprob':'1024 1024 2000 4000 %s/temp_1024 %s/power_1024 output.out',
							   'medprob':  '4096 4096 2000 4000 %s/temp_4096 %s/power_4096 output.out',
							   'largeprob':'16384 16384 2000 4000 %s/temp_16384 %s/power_16384 output.out'},

			 'rodinia_leukocyte':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/leukocyte',
							   'exe':'OpenMP/leukocyte ',
								 'exeprefix':'',
							   'suffix':'-leukocyte',
								 'datapath':'../../data/leukocyte',
								 'xtimelinesearch':'Total application run time:',
								 'maxruntime':'00:35:00',
							   'smallprob':'99 36 %s/testfile.avi',
							   'medprob':  '399 36 %s/testfile.avi',
							   'largeprob':'599 36 %s/testfile.avi'},

			 'rodinia_lud':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/lud',
							   'exe':'omp/lud_omp ',
								 'exeprefix':'',
							   'suffix':'-lud',
								 'datapath':'',
								 'xtimelinesearch':'',
								 'maxruntime':'00:45:00',
							   'smallprob':'-s 4096',
							   'medprob':  '-s 16384',
							   'largeprob':'-s 32768'},

				# Needed to modify the filelist files to contain full paths, not relative ones
				# We don't use the printed xtime from this program because it's not wall time
			 'rodinia_nn':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/nn',
							   'exe':'nn ',
								 'exeprefix':'',
							   'suffix':'-nn',
								 'datapath':'.',
								 'xtimelinesearch':'',
								 'maxruntime':'00:05:00',
							   'smallprob':'%s/filelist_4 10 30 90',
							   'medprob':  '%s/filelist_160k 10 30 90',
							   'largeprob':'%s/filelist_2560k 10 50 90'},

			 'rodinia_nw':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/nw',
							   'exe':'needle ',
								 'exeprefix':'',
							   'suffix':'-nw',
								 'datapath':'',
								 'xtimelinesearch':'Total time:',
								 'maxruntime':'00:05:00',
							   'smallprob':'23000 10 36',
							   'medprob':  '33000 10 36',
							   'largeprob':'46000 10 36'},

			 'rodinia_pathfinder':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/pathfinder',
							   'exe':'pathfinder ',
								 'exeprefix':'',
								 'datapath':'',
							   'suffix':'-pathfinder',
								 'maxruntime':'00:05:00',
							   'smallprob':'2500 2500 > /dev/null',
							   'medprob':  '5000 5000 > /dev/null',
							   'largeprob':'10000 10000 > /dev/null'},

			 #'rodinia_sradv1':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/srad/srad_v1',
				#			   'exe':'srad ',
				#				 'exeprefix':'',
				#			   'suffix':'-sradv1',
				#				 'datapath':'',
				#				 'maxruntime':'00:15:00',
				#			   'smallprob':'10 0.5 5002 5002 36',
				#			   'medprob':  '100 0.5 5002 5002 36',
				#			   'largeprob':'1000 0.5 5002 5002 36'},

			 #'rodinia_sradv2':{'exedir':'/g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/srad/srad_v2',
				#			   'exe':'srad ',
				#				 'exeprefix':'',
				#			   'suffix':'-sradv2',
				#				 'datapath':'',
				#				 'maxruntime':'00:15:00',
				#			   'smallprob':'4096 4096 0 127 0 127 36 0.5 1000',
				#			   'medprob':  '8192 8192 0 127 0 127 36 0.5 1000',
				#			   'largeprob':'8192 8192 0 127 0 127 36 0.5 10000'},

				# Need to copy the ./pots/* data files into the comd-VA-oracle and comd-PA-oracle folders
	'comd':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/CoMD/omp',
							'exe':'CoMD-openmp ',
							'exeprefix':'',
							'suffix':'-comd',
							'datapath':'',
							'xtimelinesearch':'',
							'maxruntime':'00:30:00',
							'smallprob':'-e -i 1 -j 1 -k 1 -x 50 -y 50 -z 50',
							'medprob':  '-e -i 1 -j 1 -k 1 -x 100 -y 100 -z 100',
							'largeprob':'-e -i 1 -j 1 -k 1 -x 200 -y 200 -z 200'},

	'minife':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/miniFE/omp',
							'exe':'miniFE.x ',
							'exeprefix':'',
							'suffix':'-minife',
							'datapath':'',
							'xtimelinesearch':'',
							'maxruntime':'00:20:00',
							'smallprob':'-nx 128',
							'medprob':  '-nx 256',
							'largeprob':'-nx 400'},

# SimpleMOC was modified to have 10 iterations (num_iters=10)
# This makes all the runs like 130s long...
#	'simpleMOC':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/SimpleMOC/omp',
#							'exe':'SimpleMOC ',
#							'exeprefix':'',
#							'suffix':'-simplemoc',
#							'smallprob':'-s -t 9',
#							'medprob':  '-s -t 18',
#							'largeprob':'-s -t 36'},


	'amg':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/AMG/omp',
							'exe':'amg ',
							'exeprefix':'srun -n1 -N1 ',
							'suffix':'-amg',
							'datapath':'',
							'xtimelinesearch':'wall clock time',
							'maxruntime':'00:15:00',
							'smallprob':'-problem 1 -n 128 128 128',
							'medprob':  '-problem 1 -n 256 256 256',
							'largeprob':'-problem 1 -n 400 400 400'},

			 'quicksilver':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/Quicksilver/omp',
							        'exe':'qs ',
											'exeprefix':'',
							        'suffix':'-qs',
											'datapath':'',
											'xtimelinesearch':'',
											'maxruntime':'00:15:00',
							        'smallprob':'--nSteps 60',
							        'medprob':  '--nSteps 120',
							        'largeprob':'--nSteps 240'},

			 'xsbench':{'exedir':'/g/g15/bolet1/workspace/faros/FAROS/bin/XSBench/omp',
							    'exe':'XSBench ',
									'exeprefix':'',
							    'suffix':'-xsbench',
									'datapath':'',
									'xtimelinesearch':'Runtime:',
									'maxruntime':'00:10:00',
							    'smallprob':'-m event -t 36 -k 1 -s small',
							    'medprob':  '-m event -t 36 -k 1 -s large',
							    'largeprob':'-m event -t 36 -k 1 -s XL'},

			 'lulesh':{'exedir':'/g/g15/bolet1/workspace/lulesh-region-fix-correct/LULESH/build',
							    'exe':'lulesh2.0 ',
									'exeprefix':'',
							    'suffix':'-lulesh',
									'datapath':'',
									'xtimelinesearch':'Elapsed time',
									'maxruntime':'01:00:00',
							    'smallprob':'-s 30 -r 100 -b 0 -c 8 -i 1000',
							    'medprob':  '-s 55 -r 100 -b 0 -c 8 -i 1000',
							    'largeprob':'-s 80 -r 100 -b 0 -c 8 -i 1000'}
			 }