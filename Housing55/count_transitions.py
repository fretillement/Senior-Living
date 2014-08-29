import pandas as pd 
import os
import gc
gc.collect()
''' 
This script counts the housing transitions of the elderly in 
a raw PSID dataset (current file = J177301.txt)
'''

# Label PSID housing structure variables 
namesdict = {1.0: 'Single-family house', 
			 2.0: 'Duplex/ 2-family house', 
			 3.0: 'Multifamily', 
			 4.0: 'Mobile Home/ trailer', 
			 5.0: 'Condo', 
			 6.0: 'Townhouse', 
			 7.0: 'Other', 
			 8.0: "Don't know", 
			 9.0: "Refused" 
			 }


# Extract info about elderly only 
#execfile(panel_code)


# Add var from the panel dataset to a countTransitions df
def varLookUp(row, namestub, namestub_df):
	
	# Identify year and id to look for 
	year = int(row['year'])
	unique_pid = int(row['unique_pid'])

	# Extract the value of a variable based on the year and id of obs
	if namestub+str(year) in namestub_df.columns.tolist(): 
		val = namestub_df.loc[namestub_df['unique_pid']==unique_pid, namestub+str(year)]
	else: 
		val = 0

	# Update and return the row
	row[namestub] = int(val)
	return row

# Pull info about a panel var given a group of obs in a transitions df
def varPull(group, namestub, namestub_df): 
	# For each year, look up value of namestub
	fn = lambda x: varLookUp(x, namestub, namestub_df)
	
	# Update and return this group of obs
	group = group.groupby('year').apply(fn)
	return group

# Identify members of the panel who have been institutionalized
# Based on method outlined in Ellwood and Keane (1990)
def identifyInst(transitionsdf):
	# Check if person has moved
	moved = transitionsdf['moved'] == 1

	# Check for involuntary reasons for moving
	reason = transitionsdf['whymoved'] == 7

	# Check number of rooms (must be <= 2) 
	rooms = transitionsdf['numrooms'] <= 2

	# Check that the housing structure is "other"
	hstructure = transitionsdf['Other'] == 1

	# Check for senior-housing self-report
	seniorhousing = transitionsdf['seniorh'] == 1

	# Check for institutionalization variable (1984-)
	selfinst = (transitionsdf['tinst'] == 3) | (transitionsdf['tinst'] == 7) | (transitionsdf['tinst'] == 9)

	# Check that the hh size never grows past 1 before move
	# hhsizegr = transition['famsize']

	# Update and return the transitionsdf
	transitionsdf['inst'] = (moved & reason & rooms & hstructure) | (seniorhousing) | (selfinst)
	return transitionsdf



# Generate a total num_transitions var
def totalTransitions(df):
	transitions = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
	df['num_transitions'] = transitions.apply(lambda x: x.nunique()-1, axis=1)
	return df


# Generate dummy vars for each type of transition (1-9)
def countTransitions(df, namesdict): 
	# Takes a df with housing structure vars and person id
	# Returns df with dummies for each type of transition entered

	# Stack obs in transition df by unique_pid 
	hstructure_cols = [x for x in df.columns.tolist() if 'hstructure' in x]
	hstructure = df.loc[:, hstructure_cols+['unique_pid']]
	st = pd.DataFrame(hstructure.set_index('unique_pid').stack(), columns=['hstructure'])

	# Reset index for pivoting. Creates 'index' var and removes hierarchical indexing
	st.reset_index(inplace=True)
	st.reset_index(inplace=True)

	# Pivot the observations 
	piv = st.pivot(index='index', columns='hstructure', values='unique_pid')
	if 5 not in piv: 
		piv[5] = 0

	# Rename the columns
	piv = piv.rename(columns=namesdict)

	# Convert the info in pivoted df to dummy vars
	piv['unique_pid'] = piv.max(axis=1, skipna=True)
	piv.fillna(0, inplace=True)
	#piv = piv.drop(labels=[0], axis=1)

	pivcols = [x for x in namesdict.values() if x in piv.columns.tolist()]
	for x in namesdict.values(): 
		if x not in piv: print x

	piv[piv.loc[:, pivcols]>0] = 1
	
	# Add a year variable
	st['year'] = st['level_1'].str[10:].astype(float)
	apiv = st.pivot(index='index', columns='hstructure', values='year')
	apiv['year'] = apiv.max(axis=1, skipna=True)
	piv['year'] = pd.Series(apiv['year'])			 
	
	# Return	
	return piv 

# Add age variable to a countTransitions df
def ageLookup(row, age_df):
	# This function takes a row, and looks up a person's
	# age based on unique_pid and year		
	# Construct the agevar based on the year in this row
	year = int(row['year'])
	agevar = 'age'+str(year)	
	
	# Look up the person's unique_pid
	pid = row['unique_pid']

	# Grab information about the person based on her unique_pid	
	person = age_df.loc[age_df['unique_pid'] == pid]	
	agevalue = person.reset_index().loc[0, agevar]

	# Return the row
	return agevalue

# The next two functions fill in missing age observations
# based on a single age provided and the year variable
def fillAges(group): 
	# Print the person's id
	#print group['unique_pid'].get_values()[0]
	group.reset_index(inplace=True, drop=True)

	first = group['age'].loc[group['age']>0].first_valid_index()
	last = group['age'].loc[group['age']>0].last_valid_index()	
	l = len(group['age'].index)
	
	# Check for missing observations. If none missing return same age values.
	if (first > 0) and (last+1 < l): 
		group['age2'] = len(group.index)*[999]
		return group
	if (first + last + 1 == l):
		group['age2'] = group['age']
		return group
	if (first + last + 1 > l):
		# If missing values, call algo to fill in values
		group['age2'] = calcAges(group, first, last, l)
		return group

def calcAges(gr, first, last, l): 	
	# Calculate age based on the first and last complete age observation
	o = gr['age'].loc[gr['age']>0].tolist()
	tempage = int(gr['age'][first])

	while (first > 0):
		# While there are missing values, iterate over the empty values 
		thisyr = gr.ix[first ,'year']
		prevyr = gr.ix[first-1, 'year']

		# Calculate age by subtracting difference between years from current age 
		tempage = tempage - (thisyr-prevyr)

		# If the age is 999, fill in all values as 999 
		if tempage == 999: tempage = 0 + tempage
		o = [tempage]+o
		first -= 1

	# Return a list of filled in ages 
	return o

# Takes a df of location vars for a given person, 
# and returns a list of years and transition locations
def movedWhere(locations):

	# Transpose and loop thru the locations df by year 
	piv = locations.T
	piv = piv.sort().iteritems()
	years = []
	trans = []

	# For each year, append the year and location to a list
	for pair in piv: 
		(index, df) = pair
		if df['seniorh'] == 1: 
			df = df.loc[df>0]
			years.append(int(df.ix['year'])) 
			trans.append('Senior housing')
		else: 
			df = df.loc[df>0]
			years.append(int(df.ix['year'])) 
			index = df.loc[df==1].index.tolist()
			if len(index) > 0: trans.append(index[0])
			else: trans.append("No info") 

	# Return the years and associated transition locs
	return (years, trans)


# Takes a group of obs for a certain person, and returns
# a dict with the number, ages, and types of transitions attached to the id.
def numMoves(group):
	# Get the housing vars of interest 
	housingcols = namesdict.values() + ['seniorh', 'year']

	# Count the number of transitions
	numtrans = len(group.loc[(group['moved'] == 1)])

	# Extract the person's unique id
	pid = int(group['unique_pid'].iloc[0,'unique_pid'])
	
	# Extract the ages and locations of each transition 
	ages = map(int, pd.Series(group.loc[(group['moved']==1), 'age2']).tolist())
	locations = group.loc[(group['moved']==1), housingcols]
	
	# Map each transition to its location, esp. to senior housing 
	transitions = movedWhere(locations)
	n = len(transitions[1])
	transdict = {'numtrans': numtrans, 'unique_pid': pid}
	
	# If the person has 1+ transitions, arrange the age and location of each transition in a dict
	if n > 0:
		labels = ['trans'+ str(x) for x in range(1,n+1)] + ['age_trans' + str(x) for x in range(1, n+1)]
		transinfo = dict(zip(labels, transitions[1] + ages))
		transdict.update(transinfo)
	'***Printing pid***'
	print pid

	# Return the dict as a dataframe 
	return pd.DataFrame(pd.Series(transdict)).T
	
def ageElderlyTrans(row): 
	# Identify transitions past the age of 50
	basic = {'unique_pid': row['unique_pid'], 'numtrans': row['numtrans']}

	info = row[['age_trans'+ str(x) for x in range(1,25)]].dropna().to_dict()
	list_info = info.items()

	# First get age of transitions if they occurred after age 50
	ageinfo = {'55plus_age' + str(list_info.index(i)+1): i[1] for i in info.items() if i[1] >= 50}
		
	# Get location info if transitions occurred past 50
	locinfo = {'55plus_loc' + str(list_info.index(i)+1): row['trans'+str(list_info.index(i)+1)] for i in info.items() if i[1] >= 50}
	#locinfo.update(ageinfo)
	
	if row['numtrans'] > 0: 
		# Attach ID and total number of trans; return info
		basic.update(locinfo)
		basic.update(ageinfo)

		# Reorder column names
		cols = zip(locinfo.keys(), ageinfo.keys())
		index = basic.keys()
		for x in cols: 
			index.append(x[0])
			index.append(x[1])
		index = list(reversed(index))
		return pd.Series(basic, index=index).T

	# If there are no trans past age of 55, return id and total trans
	else: 
		
		return pd.Series(basic)




if __name__ == "__main__":

	# Set filepaths
	#out = "M:/Senior Living/Data/PSID Data/Panel/transitions.csv"
	out = "/Users/ShruthiVenkatesh/Desktop/transitions00-11.csv"
	#panel_code = "M:/Senior Living/Code/Senior-living/Housing55/get_panel.py"
	paneldata ="/users/ShruthiVenkatesh/Desktop/elderly_panel00-11.csv"
	#paneldata = "M:/Senior Living/Data/PSID Data/Panel/elderly_panel00-11.csv"
	#vardata = "M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv"

	# Read in data 	
	print "Reading data"
	df = pd.read_csv(paneldata)
	agecols = [x for x in df.columns.tolist() if 'age' in x]
	age_df = df.loc[:, ['unique_pid']+agecols]

	# Create transitions spreadsheet (stacked info)
	print "Filling in age values"
	tcounts = countTransitions(df, namesdict)
	fn = lambda x: ageLookup(x, age_df)
	tcounts['age'] = tcounts.apply(fn, axis=1)
	tcounts.set_index('unique_pid', inplace=True, drop=False)
	transitions = tcounts.groupby('unique_pid').apply(fillAges)
	transitions = transitions.loc[:, ['unique_pid', 'age', 'age2', 'year']+namesdict.values()]
	#df_output.to_csv(out, index=False, columns=['unique_pid', 'age', 'age2']+namesdict.values())
	print transitions.columns.tolist()
	transitions.to_csv(out)

	# Update the transitions dataframe with inst vars for Ellwood and Kane 1990 
	transitions = pd.read_csv(out)
	namestub_list = ['numrooms', 'famsize', 'moved', 'whymoved']
	print transitions.columns.tolist()
	#namestub_list = ['tinst']
	for namestub in namestub_list: 
		print namestub
		namestubcols = [x for x in df.columns.tolist() if namestub in x]
		namestub_df = df.loc[:, ['unique_pid']+namestubcols]
		fn = lambda x : varPull(x, namestub, namestub_df)
		transitions = transitions.groupby('unique_pid').apply(fn)
	transitions.to_csv(out)

	transitions = pd.read_csv(out)
	


	#df = pd.read_csv('M:/Senior living/Data/psid data/panel/transonly.csv')
	#row = df.ix[59,:]
	##print row
	#print ageElderlyTrans(row)
	#output = df.apply(ageElderlyTrans, axis=1)
	#output.to_csv("M:/test.csv")













	
	

	
	

	#output = identifyInst(transitions)
	
	#gr = transitions.groupby('unique_pid')
	#transinfo = gr.apply(numMoves)
	#output = df.merge(transinfo, on='unique_pid')
	#group = gr.get_group(3)
	#print numMoves(group)

	#test = numMoves(group)
#	print paneldata.head()
#	test = gr.apply(numMoves)
#	print test.head()

	#output.to_csv('M:/Senior Living/Data/Psid data/Panel/elderly_trans2.csv', index=False)



	
	