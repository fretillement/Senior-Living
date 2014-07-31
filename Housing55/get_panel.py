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
allvars = pd.read_csv(vfpath, index_col='year')
varlist = list(set(itertools.chain(*(allvars.values))))

# Isolate vars from main dataset
master = pd.read_csv(dfpath, usecols=varlist)

# Keep only obs past the age of lower
agevar = allvars['age'][years[len(years)-1]]
output = master.loc[master[agevar] >= lower]

# Outsheet 
output.to_csv(ofpath, index=False)