import pandas as pd


''' 
This script arranges the raw PSID data 
(current file = J176012.txt) into a panel of senior citizen obs. 

Key variables: house type, senior housing status, 
housing tenure, type of senior housing
'''
# Edit filepaths below 
vfpath = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
dfpath = 'M:/Senior Living/Data/PSID Data/J176012.csv'
ofpath = 'M:/Senior Living/Data/PSID Data/Panel/elderly_panel.csv'

# Choose age limit and timespan 
lower = 50
years = range(1975, 1989) + range(1999, 2012, 2)
skip = range(1, min(years) - 1968 +1) if min(years) <= 1999 else "Error in years assignment"

# Find varlabels across time for years above
vardict = {}
allvars = pd.DataFrame.to_dict(pd.read_csv(vfpath, index_col=0, skiprows=skip))

#varlist = list(set(itertools.chain(*(allvars.values))))
for k in allvars: 
	for l in allvars[k]:
		vardict.update(dict(zip([allvars[k][l]],[k+str(l)])))

# Isolate vars from main dataset
master = pd.read_csv(dfpath, usecols=vardict.keys())

# Keep only obs past the age of lower
output = master.loc[(master['ER30191'] >= lower) \
				| (master['ER30220'] >= lower) \
				| (master['ER30249'] >= lower) \
				| (master['ER30286'] >= lower) \
				| (master['ER30316'] >= lower) \
				| (master['ER30346'] >= lower) \
				| (master['ER30376'] >= lower) \
				| (master['ER30402'] >= lower) \
				| (master['ER30432'] >= lower) \
				| (master['ER30466'] >= lower) \
				| (master['ER30501'] >= lower) \
				| (master['ER30538'] >= lower) \
				| (master['ER30573'] >= lower) \
				| (master['ER30609'] >= lower) \
				| (master['ER30645'] >= lower) \
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
				| (master['ER34104'] >= lower) ]

# Rename column names
for v in output: 
	output.rename(columns={v: vardict[v]}, inplace=True)

# Create unique id
output['unique_pid2'] = output.personnum2011.map(str)+ "_" + output.id19682011.map(str)
output['unique_pid'] = output.index+1

# Reorder column names
header = output.columns.tolist()
cols = ['unique_pid']+ ['id19682011']+ ['personnum2011']+\
		[x for x in header if 'htenure ' in x]+ \
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

'''
Age codes for 1968-1975
(master['ER30004'] >= lower) \
				| (master['ER30023'] >= lower) \
				| (master['ER30046'] >= lower) \
				| (master['ER30070'] >= lower) \
				| (master['ER30094'] >= lower) \
				| (master['ER30120'] >= lower) \
				| (master['ER30141'] >= lower) \
				| (master['ER30163'] >= lower) \
				|
''' 