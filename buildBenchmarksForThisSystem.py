import os
import subprocess, shlex
import argparse
from new_benchmarks import *
import sys
import time
import pandas as pd
import re
from pathlib import Path

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

rootdir = rootdirs[hostname]

# logfile
mystdout = open(APOLLO_DATA_COLLECTION_DIR+'/buildlog_'+str(hostname)+'.txt', 'w')
print('Building for ', hostname, 'in', rootdir, 'writing compiler output to:', mystdout.name)

# get the environment variables we are going to use
vars_to_use = {**os.environ.copy()}

prognames = list(progs.keys())

# Execute all the clean commands for all the benchmarks
# we perform all the cleaning before building because some
# benchmarks (e.g: NAS) share a clean command for cleaning
# everything, so we don't want to build one code, clean, and
# end up deleting the previously-built codes inadvertently.
for progname in prognames:
	prog = progs[progname]
	cleandir = rootdir+prog['cleandir']
	cleancmd =         prog['cleancmd']

	# Let's go to the cleaning directory
	os.chdir(cleandir)
	print('[%s] going to execute clean command: "%s"'%(progname, cleancmd))
	subprocess.call(cleancmd, env=vars_to_use, stdout=mystdout, stderr=mystdout, shell=True)


# Now let's build each of the codes
for progname in prognames:
	prog = progs[progname]
	builddir = rootdir+prog['builddir']
	buildcmd =         prog['buildcmd']

	# Let's go to the build directory
	os.chdir(builddir)
	print('[%s] going to execute build command: "%s"'%(progname, buildcmd))
	subprocess.call(buildcmd, env=vars_to_use, stdout=mystdout, stderr=mystdout, shell=True)


mystdout.close()

# Now let's check that each of the executable files was generated
for progname in prognames:
	prog = progs[progname]
	exedir = rootdir+prog['exedir']
	exe = prog['exe']
	smallprob = prog['smallprob']
	medprob = prog['medprob']
	largeprob = prog['largeprob']

	# if the executable is empty, check that the small, med, large problems exist
	if exe == '':
		#print()
		small_file = os.path.abspath(exedir+'/'+smallprob.rstrip())
		med_file = os.path.abspath(exedir+'/'+medprob.rstrip())
		large_file = os.path.abspath(exedir+'/'+largeprob.rstrip())
		#print(small_file)
		#print(med_file)
		#print(large_file)
		if not (os.path.exists(small_file) and os.path.exists(med_file) and os.path.exists(large_file)):
			print('[%20s] Executable DOES NOT EXIST!!!!!!!!'%(progname))
		else:
			print('[%20s] Executable EXISTS!'%(progname))

	else:
		#print()
		exe_file = os.path.abspath(exedir+'/'+exe.rstrip())
		#print(exe_file)
		if not (os.path.exists(exe_file)) :
			print('[%20s] Executable DOES NOT EXIST!!!!!!!!'%(progname))
		else:
			print('[%20s] Executable EXISTS!'%(progname))
