import pandas as pd
import itertools

''' 
This script arranges the raw PSID data 
(current file = J176012.txt) into a panel of senior citizens. 

Key variables: house type, senior housing status, 
housing tenure, type of senior housing
'''
# Choose variable 
varlabel = 'htenure'

# Edit filepaths below 
vfpath = 'M:/Senior Living/Data/PSID Data/agecohort_vars.csv'
dfpath = 'M:/Senior Living/Data/PSID Data/J176012.csv'
ofpath = 'M:/Senior Living/Data/PSID Data/Panel/pan_'+varlabel+'.csv'

# Choose age limit and timespan 
lower = 50
years = range(1991, 1998) + range(1999, 2012, 2)

# Find varlabels across time 
vardict = {}
allvars = pd.DataFrame.to_dict(pd.read_csv(vfpath, index_col='year'))
#varlist = list(set(itertools.chain(*(allvars.values))))
for k in allvars: 
	for l in allvars[k]:
		vardict.update(dict(zip([allvars[k][l]],[k+str(l)])))

# Isolate vars from main dataset
master = pd.read_csv(dfpath, usecols=vardict.keys())

# Keep only obs past the age of lower
output = master.loc[master['ER34104'] >= lower]

# Rename column names
for v in output: 
	output.rename(columns={v: vardict[v]}, inplace=True)

# Outsheet 
output.to_csv(ofpath, index=False)