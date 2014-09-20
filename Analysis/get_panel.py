import pandas as pd


''' 
This script arranges the raw PSID data 
(current file = J177301.txt) into a panel of senior citizen obs. 

Key variables: house type, senior housing status, 
housing tenure, type of senior housing
'''
# Edit filepaths below 
#vfpath = '/users/shruthivenkatesh/desktop/Senior-Living/Psid_clean/agecohort_vars.csv'
vfpath = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
#dfpath = '/users/shruthivenkatesh/desktop/J177301.csv'
dfpath = 'M:/Senior Living/Data/PSID Data/J177301.csv'
#ofpath = '/users/shruthivenkatesh/desktop/elderly_panel00-11.csv'
#ofpath = 'M:/Senior Living/Data/PSID Data/Panel/elderly_panel75-84.csv'
ofpath = 'M:/Senior Living/Data/PSID Data/Panel/over25_68-75.csv'

# Choose age limit and timespan 
lower = 25
#years = range(2001,2012,2)
#years = range(2001,2012, 2)
#years = range(1975, 1985)
#years = range(1975, 1999) + range(1999, 2012, 2)
#skip = range(1, min(years) - 1968 +1) if min(years) <= 1999 else "Error in years assignment"
years = range(1968,1976)

# Find varlabels across time for years above
vardict = {}
vardf = pd.read_csv(vfpath).fillna(0)
vardf = vardf.loc[vardf['year'].isin(years), :]
vardf = vardf.set_index('year')
allvars = pd.DataFrame.to_dict(vardf)

#print allvars

#varlist = list(set(itertools.chain(*(allvars.values))))
for k in allvars: 
	#print k
	#print allvars[k]
	for l in allvars[k]:
		if allvars[k][l] != 0 and allvars[k][l] not in vardict: vardict.update(dict(zip([allvars[k][l]],[k+str(l)])))

#print [x for x in vardict.values() if 'personnum' in x]
# Isolate vars from main dataset
print "Reading raw PSID data for all years"
master = pd.read_csv(dfpath, usecols=vardict.keys())

# Keep only obs past the age of lower
# Get a set of age codes that we should be looking for 
agecodes = vardf['age'].tolist()
agesonly = master.loc[:, agecodes]
agesonly = agesonly > lower
output = master.loc[(agesonly.sum(axis=1) > 0), :]


# Rename column names
print "Renaming columns"
for v in output: 
	if vardict[v] == 'id19681984': print vardict[v]
	output.rename(columns={v: vardict[v]}, inplace=True)

# Reorder column names
header = output.columns.tolist()


containedyrs = map(int, vardf.index.tolist())

cols = ['unique_pid']+ ['unique_pid2'] + ['id1968'+str(max(containedyrs))]+ ['personnum'+str(min(containedyrs))]+\
		[x for x in header if 'htenure' in x]+ \
		[x for x in header if 'hstructure' in x]+ \
		[x for x in header if 'seniorh' in x and 't_seniorh' not in x]+ \
		[x for x in header if 't_seniorh' in x]+ \
		[x for x in header if 'age' in x]+ \
		[x for x in header if 'indweight' in x]+ \
		[x for x in header if 'famwt' in x]+ \
		[x for x in header if 'seqnum' in x]+ \
		[x for x in header if 'relhead' in x]+ \
		[x for x in header if 'famintnum' in x] + \
		[x for x in header if 'famsize' in x] + \
		[x for x in header if 'numrooms' in x] + \
		[x for x in header if 'moved' in x and 'whymoved' not in x] + \
		[x for x in header if 'whymoved' in x]+\
		[x for x in header if 'tinst' in x]

# Create unique id
print "Creating unique ID var"
output.reset_index(inplace=True)
for x in output.columns.tolist(): 
	if 'personnum' in x: personnum = x
	if 'id1968' in x: idvar = x
output['unique_pid2'] = output[personnum].map(str)+ "_" + output[idvar].map(str)
output['unique_pid'] = output.index+1
output = output.drop('index', axis=1)
#print len(cols)
#print len(header)
#print len(output.columns.tolist())
output = output.ix[:,cols]

# Outsheet 
print "Outsheeting to " + ofpath
output.to_csv(ofpath, index=False)
