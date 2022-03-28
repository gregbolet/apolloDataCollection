# Apollo Data Collection Scripts
Scripts for our tests with Vanilla Apollo (VA) and Performance-Counter Apollo (PA).

Be sure to update the `benchmarks.py` script with the proper locations of your built executables.
These executables should already have been built using the Apollo-aware LLVM compiler.

Here's an example workflow with the scripts using PA:

`python3 doStaticRuns.py --usePA --singleModel`

`python3 createOracleDatasets.py --usePA`

`python3 doRunsUsingOracle.py --usePA`
