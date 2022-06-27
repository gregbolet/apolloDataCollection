#!/bin/bash

# This will setup all the env vars we need for Apollo to test with

export OMP_NUM_THREADS=36
export OMP_WAIT_POLICY="active"
export OMP_PROC_BIND="close"
export OMP_PLACES="cores"
export APOLLO_TRACE_CSV_FOLDER_SUFFIX="-test"
export APOLLO_COLLECTIVE_TRAINING=0 
export APOLLO_LOCAL_TRAINING=1 
export APOLLO_RETRAIN_ENABLE=0 
export APOLLO_STORE_MODELS=1
export APOLLO_TRACE_CSV=1
export APOLLO_SINGLE_MODEL=0 
export APOLLO_REGION_MODEL=1 
export APOLLO_GLOBAL_TRAIN_PERIOD=0
export APOLLO_POLICY_MODEL="DecisionTree,max_depth=4,explore=RoundRobin"
export APOLLO_ENABLE_PERF_CNTRS=1
export APOLLO_PERF_CNTRS_MLTPX=0
export APOLLO_PERF_CNTRS="PAPI_DP_OPS,PAPI_TOT_INS" 
#export APOLLO_POLICY_MODEL="Static,policy=0"

# Train a model after gathering X unique features for each region
export APOLLO_MIN_TRAINING_DATA=3

# Uses existing dataset to build a model prior to execution
export APOLLO_PERSISTENT_DATASETS=0

# new apollo flags
export APOLLO_OUTPUT_DIR="./my-test"
export APOLLO_DATASETS_DIR="my-datasets"
export APOLLO_TRACES_DIR="my-traces"
export APOLLO_MODELS_DIR="my-models"
