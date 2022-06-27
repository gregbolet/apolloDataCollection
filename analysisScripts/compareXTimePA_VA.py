import os
import argparse
import sys
import time
import pandas as pd
import re
from pathlib import Path

pd.set_option('display.max_rows', None)

APOLLO_DATA_COLLECTION_DIR='/usr/WS2/bolet1/apolloDataCollection'
#APOLLO_DATA_COLLECTION_DIR='/g/g15/bolet1/workspace/apolloDataCollection/finalData/quartz/static_runs_no_traces'

# Open the PA and VA csv files
VAdf = pd.read_csv(APOLLO_DATA_COLLECTION_DIR+'/static-ETE-XTimeData_VA.csv')
PAdf = pd.read_csv(APOLLO_DATA_COLLECTION_DIR+'/static-ETE-XTimeData_PA.csv')

print('Datasets loaded!')

# Join both datasets together into one
VAdf['type'] = 'VA'
PAdf['type'] = 'PA'

# Just one dataframe to worry about now
rawdf = pd.concat([VAdf, PAdf])

# for now, let's only focus on runs with policy 0
#rawdf = rawdf.loc[rawdf['policy'] == "Static,policy=0"]
# let's drop some programs we don't care about
rawdf = rawdf.loc[rawdf['progname'] != "rodinia_backprop"]
rawdf = rawdf.loc[rawdf['progname'] != "rodinia_nn"]
rawdf = rawdf.loc[rawdf['progname'] != "rodinia_nw"]
rawdf = rawdf.loc[rawdf['progname'] != "rodinia_pathfinder"]
#rawdf = rawdf.loc[rawdf['progname'] != "rodinia_lud" & ]

# Let's preprocess and remove runs that don't have the same counts
grouped = rawdf.groupby(['progname', 'probSize', 'policy', 'type'])

#print(grouped['type'].count())
counts = grouped.count().reset_index()
print(counts)

# Separate the PAs from the VAs, then subtract
vas = counts.loc[counts['type'] == 'VA']
pas = counts.loc[counts['type'] == 'PA']

# Now let's merge the datasets s.t. we enforce matching trial counts
# this df has all the overlapping cases with the same trial count
# from VA and PA
filtered = pd.merge(vas, pas, how='inner', on=['progname', 'probSize', 'policy', 'trialnum', 'eteXtime'])

targets = filtered[['progname', 'probSize', 'policy']]

# Now let's filter out the parent dataframe
df = pd.merge(targets, rawdf, how='inner', on=['progname', 'probSize', 'policy'])
df = df.sort_values(by=['progname', 'probSize', 'policy', 'trialnum', 'type'])
print(df.head())

# Now that we've cleaned the dataset, lets calculate means
grouped = df.groupby(['progname', 'probSize', 'policy', 'type'])

# Compute avrg and stddev
means = grouped['eteXtime'].mean().reset_index()
stds = grouped['eteXtime'].std().reset_index()

summdf = means.copy()
summdf.drop('eteXtime', axis=1, inplace=True)

summdf['mean_etextime'] = means['eteXtime']
summdf['std_etextime'] = stds['eteXtime']

print(summdf)

vadf = summdf.loc[summdf['type'] == 'VA']
padf = summdf.loc[summdf['type'] == 'PA']

vadf = vadf.sort_values(by=['progname', 'probSize', 'policy'])
padf = padf.sort_values(by=['progname', 'probSize', 'policy'])

# Now let's take the diffs between PA and VA mean xtimes
timeDiffs = padf['mean_etextime'].to_numpy() - vadf['mean_etextime'].to_numpy()

# If any values are greater than 0, then PA was slower
padf['pa_minus_va'] = timeDiffs
padf['va_mean_ete_xtime'] = vadf['mean_etextime'].to_numpy()

# Now let's get percent xtime diff
padf['perc_xtime_diff'] = (timeDiffs * 100) / (vadf['mean_etextime'].to_numpy())

padf = padf.sort_values(by=['perc_xtime_diff'])

print(padf)

# now let's lookat the lulesh runs
print(padf.loc[padf['progname'] == 'rodinia_lud'])

# Let's look at the outlier runs too
print(padf.loc[(padf['perc_xtime_diff'] <= -4) | (padf['perc_xtime_diff'] >= 4)])


