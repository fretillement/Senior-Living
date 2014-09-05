import pandas as pd
from count_transitions import fillAges, calcAges
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

def fillMoves(gr): 
	gr['moved'] = gr['moved'].fillna(0)
	l = len(gr.index)

	# Get the number of complete obs for moved and age vals 
	nummov = len(gr.loc[gr['moved']>0, 'moved'])
	numage = len(gr.loc[gr['age']>0, 'age'])

	# Check if moved val exists for all age vals. 
	#if nummov > numage: 
		# Fill in ages 

	#if nummov < numage: 
		#gr.loc[(gr['moved'] == 0) & (gr['age'] > 0), 'moved'] = 5

	#if nummov == numage == l: 
		# Do nothing; everything's filled in 

	#if (nummov == numage) & (nummov < l): 
		# Check for a sandwich 
		#gr.loc[gr['moved'] == 0].index() 	

	# Check if age vals all exist. 	
 
	print gr





	#print gr['moved'].reset_index(drop=False).first_valid_index()
	#print gr['moved'].reset_index(drop=False).last_valid_index()
	#if len(gr.loc[(gr['age'] == 0) & (gr['moved'] <1)].index) > 0: print gr['unique_pid2']
	#if len(gr.loc[(gr['age'] == 0) & (gr['moved'] <1)].index) > 0: print gr['unique_pid2']
	if len(gr.loc[(gr['age'] != 0) & (gr['moved'] == 0)].index) > 0: 
		print gr #gr.loc[(gr['moved'] != 0) & (gr['age'] == 0)] 
		#print gr

merged = pd.read_csv("M:/senior living/data/psid data/ages_merged.csv")
print 'Unnamed: 0' in merged
print merged.columns.tolist()
merged = merged.drop('Unnamed: 0', axis=1)
merged = merged.rename(columns = {'level_1': 'year'})

gr_merged = merged.groupby('unique_pid2')
#gr_merged.apply(fillMoves)
test = gr_merged.get_group('5904_181')
fillMoves(test)


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