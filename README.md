# Apollo Data Collection Scripts
Scripts for running tests with Apollo.

Right now we're experimenting with Bayesian Optimization and using it to do fine-grain tuning of codes instrumented with Apollo. There are a bunch of environment variables that Apollo uses which can be found in the `apolloTestEnvSetup.sh` script. If you want to run an Apollo-instrumented code, these variables should suffice.

## Using These Scripts
Right now, it is best to use the scripts in the `slurmBayesianOptim` directory since these are the most up-to-date and target the experiments we would like to perform. The other directories can be peeked at but not guaranteed to work, they are simply included for reference and if we need to re-do some experiments.

The way in which the `slurmBayesianOptim` experiments work is by taking a target program that has been instrumented with Apollo and invoking it multiple times with differetnt policy combinations in every region execution. It uses a Python Bayesian Optimization package to perform the exploration of the policy space for each region execution. 

More details to come...

### Apollo Installation
### Python Environment + Script Setups
### Performing Trials

