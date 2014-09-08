import pandas as pd
from count_transitions import fillAges, calcSandwichAges, calcOutsideAges
import gc

# Set file paths: variable codes and raw data 
var_file = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
raw_file = 'M:/Senior Living/Data/PSID Data/J177301.csv'

# Set namestub list 
namestub_list = ['id1968', 'personnum', 'hstructure', 'age', 'htenure', 'moved']

# Get codes of age, moved, hstructure, tenure and id variables 
def getCodes(varfile, namestub): 
	values = pd.read_csv(varfile, usecols = [namestub, 'year']).dropna()
	years = map(int, values['year'].tolist())
	codes = values[namestub].tolist()
	return [years, codes]

def readRaw(rawfile, varfile, namestub_list=namestub_list): 
	cols = []
	for n in namestub_list: 
		cols = getCodes(varfile, n)[1] + cols
	raw = pd.read_csv(rawfile, usecols=cols)
	# Keep only obs >= 25 at any given point 
	ages = getCodes(varfile, 'age')[1]
	raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 
	return raw

def sepFrames(rawfile, varfile, n): 
	raw = readRaw(rawfile, varfile)
	codes = getCodes(varfile, n)[1]
	ids = list(set(getCodes(varfile, 'id1968')[1])) + list(set(getCodes(varfile, 'personnum')[1]))
	sep = raw.loc[(raw['25plus'] > 0), codes + ids]
	return sep

def genUniqueID(sep): 
	sep['unique_pid2'] = sep['ER30001'].map(str)+ "_" + sep['ER30002'].map(str)
	return sep 

sep = sepFrames(raw_file, var_file, 'hstructure')
print sep.head(20)


'''
ages =  list(pd.read_csv(var_file, usecols=['age']).values.ravel())
idvars = pd.read_csv(var_file, usecols = ['id1968', 'personnum']).drop_duplicates()
moved = list( pd.read_csv(var_file, usecols = ['moved']).values.ravel())
hstructure = list(pd.read_csv(var_file, usecols = ['hstructure'].values.ravel()))
htenure = list(pd.read_csv(var_file, usecols = ['htenure']).values.ravel())
years = map(int, list(pd.read_csv(var_file, usecols=['year']).values.ravel()))

movedlabs = ['moved'+str(y) for y in years]
moveddict = dict(zip(moved, years))
yearsdict = dict(zip(ages, years))
cols = list(ages) + list(idvars.values.ravel()) + moved

# Read in age, moved, and id variables for selected years 
raw = pd.read_csv(raw_file, usecols=cols) 

# Keep observations who were 25 or older at least once across years  
raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 

# Seperate age variables from moving variables: place in seperate dataframes 
agerq = raw.loc[(raw['25plus'] > 0), ages + list(idvars.values.ravel())] 
mov = raw.loc[(raw['25plus'] > 0), moved + list(idvars.values.ravel())]
struct = raw.loc[(raw['25plus'] > 0), hstructure + list(idvars.values.ravel())]
tenure = raw.loc[(raw['25plus'] > 0), htenure + list(idvars.values.ravel())]

# Generate a unique person id number 
mov['unique_pid2'] = mov['ER30001'].map(str)+ "_" + mov['ER30002'].map(str)
agerq['unique_pid2'] = agerq['ER30001'].map(str)+ "_" + agerq['ER30002'].map(str)
struct['unique_pid2'] = struct['ER30001'].map(str)+ "_" + struct['ER30002'].map(str)
tenure['unique_pid2'] = tenure['ER30001'].map(str)+ "_" + tenure['ER30002'].map(str)

# Stack the panel datasets (each person shows up multiple times)
yearsdict.update(moveddict)
mov.rename(columns = moveddict, inplace =True)
agerq.rename(columns = yearsdict, inplace= True)
st_moved = pd.DataFrame(mov.loc[:, years +['unique_pid2']].set_index('unique_pid2').stack())
st_moved = st_moved.rename(columns = {0: "moved"})
st_agerq = pd.DataFrame(agerq.loc[:, years +['unique_pid2']].set_index('unique_pid2').stack())
st_agerq = st_agerq.rename(columns= {0: 'age'})
merged = st_agerq.merge(st_moved, how='left', right_index=True, left_index=True)
merged.reset_index(inplace=True)
merged.to_csv("M:/Senior Living/data/psid data/ages_merged_68-75.csv")

# Read in csv of stacked panel data and groupby person's id
fpath = "M:/senior living/data/psid data/ages_merged_68-75.csv"
#fpath = "/users/shruthivenkatesh/desktop/senior-living-proj/data/edited_vars.csv"
merged = pd.read_csv(fpath)
print merged.columns.tolist()
merged = merged.drop('Unnamed: 0', axis=1)
merged = merged.rename(columns = {'level_1': 'year'})
gr_merged = merged.groupby('unique_pid2')


# Identify "sandwich rows" and strip all rows 
# that are not part of a "sandwich" and have BOTH 'age'
# and 'moved' values equal to 0
def getMissingAges(gr): 
	gr = gr.fillna(0)
	if 999 in gr['age'].tolist(): 
		gr.loc[(gr['age'] == 999), 'age'] = 0
	gr = gr.reset_index()
	trailing_mask = ((gr['age'] > 0) | (gr['moved'] > 0))
	if gr.loc[trailing_mask,['age', 'moved']].empty :
		return gr.loc[trailing_mask,['age', 'moved']]
	else:
		first = gr.loc[trailing_mask,['age', 'moved']].first_valid_index()
		last = gr.loc[trailing_mask, ['age', 'moved']].last_valid_index()
		gr = gr.loc[(gr.index >= first) & (gr.index <= last), :]
		sandwich_mask = ((gr['age'].cumsum() > 0) & (gr['moved'].cumsum()>0)
			    & (gr['age'] == 0) & (gr['moved'] == 0))
		gr.loc[sandwich_mask, ['age', 'moved']] = 0
		return gr 

# Fill in ages using fillAges function from count_observations
def fillMissingAges(gr): 
	gr = getMissingAges(gr)	
	if gr.empty: 
		return gr
	else: 
		gr = fillAges(gr)
		return gr 

# Fill in missing moved observations (if age exists)
def fillMissingMoved(gr): 
	gr = fillMissingAges(gr)
	if gr.empty: 
		return gr
	else: 	
		gr['moved2'] = gr.loc[:, 'moved']
		missing_move = ((gr['moved'] == 0) & (gr['age2'] > 0))
		gr.loc[missing_move, 'moved2'] = 5
		gr = gr.loc[(gr['age2']>0), :]
		return gr







#output = gr_merged.apply(fillMissingMoved)
#print "**Writing**"
#output.to_csv("M:/Senior living/data/psid data/edited_vars_68-75.csv")
#output.to_csv("/users/shruthivenkatesh/desktop/senior-living-proj/data/edited_vars.csv")
#print fixMissing(test)
#test= fillMissingAges(test)
#print test.loc[:, ['age', 'age2', 'year', 'moved']]
#print fillMissingMoved(test)

gc.collect()

'''