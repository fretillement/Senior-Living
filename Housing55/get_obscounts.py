import pandas as pd
from count_transitions import fillAges, calcSandwichAges, calcOutsideAges
import gc
'''
# Select and read in age and id vars only 
ages =  list(pd.read_csv('M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv', usecols=['age']).values[7:].ravel())
idvars = pd.read_csv('M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv', usecols = ['id1968', 'personnum']).drop_duplicates()
moved = list( pd.read_csv('M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv', usecols = ['moved']).values[7:].ravel())
years = map(int, list(pd.read_csv('M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv', usecols=['year']).values[7:].ravel()))
movedlabs = ['moved'+str(y) for y in years]
moveddict = dict(zip(moved, years))
yearsdict = dict(zip(ages, years))
cols = list(ages) + list(idvars.values.ravel()) + moved
raw = pd.read_csv('M:/Senior Living/Data/PSID Data/J177301.csv', usecols=cols) 

# Keep ages above 25
raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 
agerq = raw.loc[(raw['25plus'] > 0), ages+list(idvars.values.ravel())] 
mov = raw.loc[(raw['25plus'] > 0), moved + list(idvars.values.ravel())]

mov['unique_pid2'] = mov['ER30001'].map(str)+ "_" + mov['ER30002'].map(str)
agerq['unique_pid2'] = agerq['ER30001'].map(str)+ "_" + agerq['ER30002'].map(str)

yearsdict.update(moveddict)

mov.rename(columns = moveddict, inplace =True)
agerq.rename(columns = yearsdict, inplace= True)

st_moved = pd.DataFrame(mov.loc[:, years +['unique_pid2']].set_index('unique_pid2').stack())
st_moved = st_moved.rename(columns = {0: "moved"})


st_agerq = pd.DataFrame(agerq.loc[:, years +['unique_pid2']].set_index('unique_pid2').stack())
st_agerq = st_agerq.rename(columns= {0: 'age'})

merged = st_agerq.merge(st_moved, how='left', right_index=True, left_index=True)
merged.reset_index(inplace=True)
merged.to_csv("M:/Senior Living/data/psid data/ages_merged.csv")
'''


# Read in csv and groupby person's id
#fpath = "M:/senior living/data/psid data/ages_merged.csv"
fpath = "/users/shruthivenkatesh/desktop/senior-living-proj/data/edited_vars.csv"
merged = pd.read_csv(fpath)
#merged = merged.drop('Unnamed: 0', axis=1)
#merged = merged.rename(columns = {'level_1': 'year'})
gr_merged = merged.groupby('unique_pid2')
test = gr_merged.get_group('1777_171')
#test = gr_merged.get_group('5904_181')

# Identify "sandwich rows" and strip all rows 
# that are not part of a "sandwich" and have BOTH 'age'
# and 'moved' values equal to 0
def getMissingAges(gr): 
	gr = gr.fillna(0)
	if 999 in gr['age'].tolist(): 
		gr.loc[(gr['age'] == 999), 'age'] = 0
	gr = gr.reset_index()
	trailing_mask = ((gr['age'] > 0) | (gr['moved'] > 0))
	first = gr.loc[trailing_mask,['age', 'moved']].first_valid_index()
	last = gr.loc[trailing_mask, ['age', 'moved']].last_valid_index()
	gr = gr.loc[(gr.index >= first) & (gr.index <= last), :]
	sandwich_mask = ((gr['age'].cumsum() > 0) & (gr['moved'].cumsum()>0)
		    & (gr['age'] == 0) & (gr['moved'] == 0))
	gr.loc[sandwich_mask, ['age', 'moved']] = 0
	return gr 

def fillMissingAges(gr): 
	gr = getMissingAges(gr)	
	gr = fillAges(gr)
	return gr 

def fillMissingMoved(gr): 
	gr = fillMissingAges(gr)
	gr['moved2'] = gr.loc[:, 'moved']
	missing_move = ((gr['moved'] == 0) & (gr['age2'] > 0))
	gr.loc[missing_move, 'moved2'] = 5
	gr = gr.loc[(gr['age2']>0), :]
	return gr

def fixAgeError(gr): 
	if 999 in gr['age'].tolist(): 
		print gr['unique_pid2'].iloc[0]
		gr.loc[(gr['age'] == 999), 'age'] = 0
		gr = fillMissingMoved(gr)	
		return gr 
	else: 
		return gr  

#output = gr_merged.apply(fillMissingMoved)
output = gr_merged.apply(fixAgeError)
print "**Writing**"
output.to_csv("/users/shruthivenkatesh/desktop/senior-living-proj/data/edited_vars.csv")
#print fixMissing(test)
#test= fillMissingAges(test)
#print test.loc[:, ['age', 'age2', 'year', 'moved']]
#print fillMissingMoved(test)

gc.collect()
'''
# Fill in ages 
gr_st_agerq = st_agerq.groupby('unique_pid2')
output = gr_st_agerq.apply(fillAges)
print output.head(30)
#output.to_csv("M:/test_agesonly.csv")

print len(raw.index)
print len(agerq.index)
print len(st_agerq.index)
'''