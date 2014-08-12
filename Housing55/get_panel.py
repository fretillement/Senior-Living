import pandas as pd


''' 
This script arranges the raw PSID data 
(current file = J176012.txt) into a panel of senior citizen obs. 

Key variables: house type, senior housing status, 
housing tenure, type of senior housing
'''
# Edit filepaths below 
vfpath = 'M:/Senior Living/Data/PSID Data/agecohort_vars.csv'
dfpath = 'M:/Senior Living/Data/PSID Data/J176012.csv'
ofpath = 'M:/Senior Living/Data/PSID Data/Panel/elderly_panel.csv'

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
output = master.loc[(master['ER34104'] >= lower) \
				| (master['ER30692'] >= lower) \
				| (master['ER30736'] >= lower) \
				| (master['ER30809'] >= lower) \
				| (master['ER33104'] >= lower) \
				| (master['ER33204'] >= lower) \
				| (master['ER33304'] >= lower) \
				| (master['ER33404'] >= lower) \
				| (master['ER33504'] >= lower) \
				| (master['ER33604'] >= lower) \
				| (master['ER33704'] >= lower) \
				| (master['ER33804'] >= lower) \
				| (master['ER33904'] >= lower) \
				| (master['ER34004'] >= lower) \
				| (master['ER34104'] >= lower)]

# Rename column names
for v in output: 
	output.rename(columns={v: vardict[v]}, inplace=True)

# Create unique id
output['unique_pid'] = output.personnum2011.map(str)+ "_" + output.id19682011.map(str)

# Reorder column names
header = output.columns.tolist()
cols = ['unique_pid']+ ['id19682011']+ ['personnum2011']+\
		[x for x in header if 'htenure' in x]+ \
		[x for x in header if 'hstructure' in x]+ \
		[x for x in header if 'seniorh' in x and 't_seniorh' not in x]+ \
		[x for x in header if 't_seniorh' in x]+ \
		[x for x in header if 'age' in x]+ \
		[x for x in header if 'indweight' in x]+ \
		[x for x in header if 'famwt' in x]+ \
		[x for x in header if 'seqnum' in x]+ \
		[x for x in header if 'relhead' in x]+ \
		[x for x in header if 'famintnum' in x]
output = output.loc[:,cols]

# Outsheet 
output.to_csv(ofpath, index=False)
