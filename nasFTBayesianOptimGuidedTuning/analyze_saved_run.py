import pandas as pd

df = pd.read_csv('./ft-medprob-savedRuns.csv')

# find the max of the first 16 trials
static = df.iloc[0:16]
worstStatic = static.iloc[static.xtime.idxmax()]

worstStaticXtime = worstStatic.xtime

print(static)
print(worstStatic)
print(worstStaticXtime)

largerXtimes = df[df['xtime'] >= worstStaticXtime]
print(largerXtimes)

print('mean xtime:', df.xtime.mean())