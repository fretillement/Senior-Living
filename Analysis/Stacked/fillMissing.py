from getStackedFrame import *
from count_transitions import *
import pandas as pd

# Fill in missing hstructure obs if the person hasn't moved
def fillHstructure(self):
	group = self
	group = group.reset_index(drop=True)
	if any(0 == group.hstructure): 
		gr_iter = group.iterrows()
		for l in gr_iter: 
			(index, row) = l 
			if (index > 0) & (row['moved2'] == 5) & (row['hstructure'] == 0): 	
				group.loc[index, 'hstructure'] = group.loc[index-1, 'hstructure']
		return group
	else: return group 	

# Identify "sandwich rows" and strip all rows 
# that are not part of a "sandwich" and have BOTH 'age'
# and 'moved' values equal to 0
def getMissingAges(self): 
	gr = self
	gr = gr.fillna(0)
	if 999 in gr['age'].tolist(): 
		gr.loc[(gr['age'] == 999), 'age'] = 0
	gr = gr.reset_index()
	trailing_mask = ((gr['obstype'].isin([0,5])))
	#trailing_mask = ((gr['age'] > 0) | ((gr.loc[:, vars_list]).sum(axis=1) > 0))
	if gr.loc[trailing_mask,['age', 'moved']].empty :
		return gr.loc[trailing_mask,:]
	else:
		first = gr.loc[trailing_mask,['age', 'moved']].first_valid_index()
		last = gr.loc[trailing_mask, ['age', 'moved']].last_valid_index()
		gr = gr.loc[(gr.index >= first) & (gr.index <= last), :]
		sandwich_mask = ((gr['age'].cumsum() > 0) & (gr['moved'].cumsum()>0)
			    & (gr['age'] == 0) & (gr['moved'] == 0))
		gr.loc[sandwich_mask, ['age', 'moved']] = 0
		return gr	

# Fill in ages using fillAges function from count_observations
def fillMissingAges(self):
	gr = self
	gr = getMissingAges(gr)	
	if gr.empty: 
		return gr
	else: 
		gr = fillAges(gr)
		return gr 		

# Fill in missing "moved" observations (if at least one other var exists)
def fillMissingMoved(self):
	gr = self
	#gr = gr.reset_index()
	#print gr['unique_pid'].iloc[0]
	#gr = gr.loc[(gr['obstype'].isin([0,5])), :]
	gr = fillMissingAges(gr)
	if gr.empty: 
		return gr
	else: 	
		gr['moved2'] = (( gr['moved'] == 1 ))
		#gr['moved2'] = gr.loc[:, 'moved']
		#missing_move = ((gr['moved'] == 0) & (gr['obstype'].isin([0,5])))
		#missing_move = ((gr['moved'] == 0))
		#gr.loc[missing_move, 'moved2'] = 0
		gr = gr.loc[(gr['age2']>0), :]
		return gr

# Implement the above functions for each person (group)
def implementFill(group):
	gr = fillMissingMoved(group)
	gr = fillHstructure(gr)
	return gr

if __name__ == '__main__':
	'''
	obstype = getStackedFrame('obstype', 'J178305').implement()
	varlist = ['age', 'indweight', 'moved', 'hstructure', 'htenure']
	for v in varlist:
		print v  
		temp =  getStackedFrame(v, 'J178305').implement()
		obstype = obstype.merge(temp, right_index=True, left_index=True, how='outer')

	obstype = obstype.reset_index()
	obstype = obstype.rename(columns={'level_1': 'year'})
	print "Writing"
	obstype.to_csv("M:/test.csv", index=False)
	print "FillMissing"

	#obstype = pd.read_csv("M:/test.csv")
	obstype = obstype.groupby('unique_pid').apply(implement)	
	obstype.to_csv("M:/test.csv", index=False)
	'''




'''











print "Stacking all variables into one df"
age = stackdf('age')
for n in vars_list: 
	print n
	age = age.merge(stackdf(n), right_index=True, left_index=True, how='outer')
print age.columns.tolist()
age.to_csv(basicvars_fpath)

print "Fill-in procedure for age and moved vars"
df = pd.read_csv(basicvars_fpath)
df = df.rename(columns={'Unnamed: 1': 'year'})
df_ages = df.groupby('unique_pid').apply(fillMissingMoved)
print "**Writing**"
df_ages.to_csv(basicvars_age_fpath, index=False)


print "Renaming/ marking housing categories"
df = pd.read_csv("M:/senior living/data/psid data/basicvars_age.csv")
print "		Identifying institutionalization"
df = anyInst(df)
df = renameHstructure(df)
print "		Filling empty hstructure obs"
df = df.groupby('unique_pid').apply(fillHstructure)
df.to_csv("M:/senior living/data/psid data/allvars_st.csv", index=False)


df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
print "  	Marking housing transition categories"
df = markHousingFrom(df)
df.to_csv("M:/senior living/data/psid data/allvars_st.csv", index=False)




def ageTrans(df): 
	df_gr = df.groupby('age2')
	
	def ageGrCount(gr): 
		age = gr['age2'].iloc[0]
		output = {age: {}}
		existingcat = gr['Housing Category'].value_counts()
		tocat = gr['Trans_to'].value_counts()
		fromcat = gr['Trans_from'].value_counts()
		numtrans = len(gr.loc[((gr['moved']==1) & (gr['Housing Category'] != 0))].index)
		for c in existingcat.index: 
			info = {c: existingcat[c]}
			output[age].update(info)
		for c in tocat.index:
			#print c
			#info = {'to_'+str(c): tocat[c]/numtrans}
			info = {'to_'+str(c): tocat[c]}
			output[age].update(info)
		for c in fromcat.index: 
			#info = {'from_'+str(c): fromcat[c]/numtrans}
			info = {'from_'+str(c): fromcat[c]}
			output[age].update(info)	
		return pd.DataFrame.from_dict(output, orient='index') 

	sharesdf = df_gr.apply(ageGrCount)
	return sharesdf

#df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
#df = df.rename(columns={'housingcategory': 'Housing Category'})
#df = mergeBeale(df)
#print "Writing"
#df.to_csv('M:/senior living/data/psid data/allvars_st_urban.csv')

df = pd.read_csv('M:/senior living/data/psid data/allvars_st_urban.csv')

urbancode_mask = ((df['urbancode'] <= 6) & (df['urbancode'] >= 1)) 
ruralcode_mask = ((df['urbancode'] >= 7)) 

urbandf = df.loc[urbancode_mask]
ruraldf = df.loc[ruralcode_mask]

#range(1968, 1985), 
ranges = [range(1985, 1996), range(1996, 2000) + range(1999, 2013, 2)]
for timespan in ranges: 
	urban_timeobs = urbandf.loc[((urbandf['year'].isin(timespan))), :] 
	rural_timeobs = ruraldf.loc[((ruraldf['year'].isin(timespan))), :] 

	urbandf_shares = ageTrans(urban_timeobs)
	ruraldf_shares = ageTrans(rural_timeobs)

	name = str(min(timespan)) + '-' + str(max(timespan))
	print name 

	urbandf_shares.to_csv("M:/senior living/data/psid data/hcatnums_urban_"+name+".csv", index=True)
	ruraldf_shares.to_csv("M:/senior living/data/psid data/hcatnums_rural_"+name+".csv", index=True)


#df_shares = ageTrans(df)
#df_shares.to_csv("M:/senior living/data/psid data/housingcat_nums.csv", index=True)

'''
