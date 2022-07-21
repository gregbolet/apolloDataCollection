#!/bin/bash
#BSUB -J Lyre_Oracle_Create # Job name
#BSUB -nnodes 1             # Maximum number of nodes to be allocated
#BSUB -W 180 								# walltime in minutes
#BSUB -q pbatch 						# queue to use 
#BSUB -oo createOracleDatasetsLog.txt
#BSUB -eo createOracleDatasetsERRORLog.txt


source ~/.profile

#lrun -N 1 -T 1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh
#lrun -N 1 -T 1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh --usePA
#lrun -1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh
#lrun -1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh --usePA

#-a is the number of tasks per resource set
#-n is the totla number of resource sets for this job
#-c is the number of cores per resource set
#-r is the number of resource sets per node
#jsrun -r1 -a1 -c38 -n1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh
date
jsrun -r1 -a1 -c38 -n1 python3 createOracleDatasets.py --onlyAllProbs --benchmarks lulesh --usePA --colsToKeep f0
date