from __future__ import division
import pandas as pd 
import os
import gc
import numpy as np 
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
# Based on method outlined in Ellwood and Kane (1990)
def identifyInst(transdf):
	# Check if person has moved
	moved = transdf['moved'] == 1

	# Check for involuntary reasons for moving
	reason = transdf['whymoved'] == 7

	# Check number of rooms (must be <= 2) 
	rooms = transdf['numrooms'] <= 2

	# Check that the housing structure is "other"
	hstructure = transdf['Other'] == 1

	# Check for senior-housing self-report
	if 'seniorh' in transdf: seniorhousing = transdf['seniorh'] == 1
	else: seniorhousing = 0

	# Check for institutionalization variable (1984-)
	if 'tinist' in transdf: selfinst = (transdf['tinst'] == 3) | (transdf['tinst'] == 7)
	else: selfinst = 0

	# Check that the hh size never grows past 1 before move
	# hhsizegr = transition['famsize']

	# Update and return the transitionsdf
	transdf['inst'] = (moved & reason & rooms & hstructure) | (seniorhousing) | (selfinst)
	return transdf



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
	for x in namesdict.keys():
		if x not in piv: 
			piv[x] = 0

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
	print (first, last, l, group['unique_pid'].ix[0])
	# Check for missing observations. If none missing return same age values.
	if group['age'].sum() == 0: 
		group['age2'] = 0
		return group
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
		years.append(int(df.ix['year'])) 
		if (df['inst'] == 1) and (df['seniorh'] == 1): 
			df = df.loc[df>0]
			trans.append('Senior housing')
		if (df['inst'] == 1) and (df['seniorh'] != 1): 
			df = df.loc[df>0]	
			trans.append('Senior inst (EK1990)')
		if (df['inst'] != 1) and (df['seniorh'] == 1): 
			df = df.loc[df>0]
			trans.append('Senior housing')
		else: 			
			df = df.loc[df>0]
			index = df.loc[df==1].index.tolist()
			if len(index) > 0: 
				if 'shared' in df and df['shared'] == 1: trans.append('Shared '+index[0])
				else: trans.append(index[0])
			else: trans.append("No info") 
	#print (years,trans)		
	# Return the years and associated transition locs
	return (years, trans)


# Takes a group of obs for a certain person, and returns
# a dict with the number, ages, and types of transitions attached to the id.
def numMoves(group):
	# Get the housing vars of interest 
	housingcols = namesdict.values() + ['shared', 'inst', 'seniorh', 'year']

	# Count the number of transitions
	numtrans = len(group.loc[(group['moved'] == 1)])

	# Extract the person's unique id
	pid = int(group['unique_pid'].iloc[0])
	
	# Extract the ages and locations of each transition 
	ages = map(int, pd.Series(group.loc[(group['moved']==1), 'age2']).tolist())
	for x in housingcols: 
		if x not in group.columns.tolist(): group[x] = 0
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
	#print pid
	# Return the dict as a dataframe 
	return pd.DataFrame(pd.Series(transdict)).T
	
# This function extracts only obs with transitions that occur
# past the age of lower (55 previously). 	
def ageElderlyTrans(row, lower, maxtrans): 
	# Initializing an identication dict
	basic = {'unique_pid': row['unique_pid'], 'numtrans': row['numtrans']}
	
	# Initialize output dicts based on the maximum number of trans possible
	agecols = [x for x in row.index if 'age_trans' in x] 
	transcols = [x for x in row.index if 'trans' in x and 'age' not in x and 'num' not in x]	
	ageoutput = {'age_trans'+str(i):0 for i in range(1,maxtrans+1)}
	locoutput = {'trans'+str(i):0 for i in range(1,maxtrans+1)}

	# If the obs has no transitions, return an empty dataframe with identification
	if row['numtrans'] < 1: 
		basic.update(ageoutput)
		basic.update(locoutput)
		return pd.Series(basic)
	
	# If the obs has at least one transition, 	
	else: 
		# For each transition present, look up the age and location and map it to the
		# output dicts by index. (i.e. a person whose 1st transition after the age of 55 was actually
		# the 5th transition of her life will be mapped to "trans1" and "age_trans1" keys.)	
		ages = row.loc[agecols].dropna()
		locs = row.loc[transcols].dropna()
		# ages and locs are the same length!!! 
		for k in range(0, len(ages)):
			agelab = 'age_trans'+str(int(k+1))
			loclab = 'trans' + str(int(k+1))
			ageoutput[agelab] = ages[k]
			locoutput[loclab] = locs[k]
		# Update the basic info dict and return as series
		basic.update(ageoutput)
		basic.update(locoutput)
		return pd.Series(basic)	

def identifyShared(transdf):
	transdf['shared'] = 0

	# For years before 1983, attach a variable that identifies
	# whether a person joined a shared household with family
	transdf.loc[(transdf['year'] < 1983), 'shared'] = transdf['relhead'].isin([4, 5, 7]) 

	# For years after 1983, attach shared variable
	after = [40, 47, 48, 50, 57, 58, 66, 67, \
			67, 68, 69, 72, 73, 74, 75, 95, 96, 97]
	transdf.loc[(transdf['year'] >= 1983), 'shared'] = transdf['relhead'].isin(after)

	return transdf

def computeTransShare(agegroup):
	age = agegroup['age2'].iloc[0]
	moved = agegroup.loc[(agegroup['moved'] == 1), 'moved'].sum()
	notmoved = agegroup.loc[(agegroup['moved'] == 5), 'moved'].sum()
	share = moved/ notmoved
	numpeople = len(agegroup.index)
	output = pd.DataFrame({'age2': age, 'sh_trans':share, 'numobs':numpeople}, index = [0])
	return output

if __name__ == "__main__":
	# Set lower age limit
	lower = 55

	# Get the date csv file suffix
	#datestrings = ['75-84', '85-99', '01-11']
	datestrings = ['75-84']
	for date in datestrings: 
		print "Processing transitions for years "+ date
		
		# Set filepaths
		#out = "M:/Senior Living/Data/PSID Data/Panel/transitions" + date + ".csv"
		#out = "/Users/ShruthiVenkatesh/Desktop/transitions00-11.csv"
		out = 'M:/Senior Living/Data/PSID Data/Panel/transitions25.csv'
		#panel_code = "M:/Senior Living/Code/Senior-living/Housing55/get_panel.py"
		#paneldata ="/users/ShruthiVenkatesh/Desktop/elderly_panel00-11.csv"
		paneldata = 'M:/Senior Living/Data/PSID Data/Panel/over25.csv'
		#paneldata = "M:/Senior Living/Data/PSID Data/Panel/elderly_panel" + date + ".csv"
		out_movespanel = "M:/Senior Living/Data/PSID Data/Panel/elderly_panelv2_" + date + ".csv"
		out_55pluspanel = "M:/Senior Living/Data/PSID Data/Panel/55plus_trans" + date + ".csv"

		# Read in data 	
		print "Reading master data"
		df = pd.read_csv(paneldata)
		agecols = [x for x in df.columns.tolist() if 'age' in x]
		age_df = df.loc[:, ['unique_pid']+agecols]
		'''
		# Create transitions spreadsheet (stacked info)
		print "Filling in age values"
		tcounts = countTransitions(df, namesdict)
		tcounts.to_csv(out, index=False)
		print "Done counting transitions"
		fn = lambda x: ageLookup(x, age_df)
		tcounts['age'] = tcounts.apply(fn, axis=1)
		tcounts.to_csv(out, index=False)
		print "Done looking up ages"
		
		tcounts = pd.read_csv(out)
		tcounts.set_index('unique_pid', inplace=True, drop=False)
		transitions = tcounts.groupby('unique_pid').apply(fillAges)
		transitions = transitions.loc[:, ['unique_pid', 'age', 'age2', 'year']+namesdict.values()]
		transitions.to_csv(out)
		
		
		# Update the transitions dataframe with institutional housing identification vars 
		# Based on Ellwood and Kane (1990) 
		print "Updating transitions dataframe with inst identification vars"
		transitions = pd.read_csv(out)
		#namestub_list = ['numrooms', 'famsize', 'moved', 'whymoved', 'seniorh', 'relhead']
		namestub_list = ['moved']
		for namestub in namestub_list: 
			print "		Adding " + namestub
			namestubcols = [x for x in df.columns.tolist() if namestub in x and 't_'+namestub not in x]
			namestub_df = df.loc[:, ['unique_pid']+namestubcols]
			fn = lambda x : varPull(x, namestub, namestub_df)
			transitions = transitions.groupby('unique_pid').apply(fn)
		print "		Identifying institutions"
		#transitions = identifyInst(transitions)
		print "		Identifying shared households"
		#transitions = identifyShared(transitions)
		transitions.to_csv(out, index=False)
		print transitions.head(30)
		'''
		transitions = pd.read_csv(out)
		gr = transitions.groupby('age2')
		output = gr.apply(computeTransShare)
		output = output.loc[output['age2'].isin(range(25, 100)), :]
		output.to_csv("M:/Senior Living/Data/PSID Data/share_trans25.csv", index=False)

		'''
		# Total up the number and type of moves
		# Attach this to the original panel variables
		print "Totaling up the number of moves and housing type of each move"
		transitions = pd.read_csv(out)	
		gr = transitions.groupby('unique_pid')
		transinfo = gr.apply(numMoves)
		output = df.merge(transinfo, on='unique_pid')
		#output = output.reset_index()
		print output.columns.tolist()
		output.to_csv(out_movespanel)
		
	
		# Isolate ONLY the people who had a transition after the age of 55
		# Get the maximum number of transitions that took place
		# after an individual was over the age of lower		
		print "Isolating observations to only people who transitioned after the age of "+ str(lower)
		panel = pd.read_csv(out_movespanel)
		#trans = panel.loc[panel['numtrans'] > 0, :] 
		age_df = panel.loc[:, [x for x in panel.columns.tolist() if 'age_trans' in x]]
		fn = lambda x: sum(x.isin(range(lower, 400)))
		panel['elderly'] = age_df.apply(fn, axis=1)
		agequals = panel.loc[panel['elderly']>0, :]
		maxtrans = agequals['elderly'].max()		
		fn = lambda x : ageElderlyTrans(x, lower, maxtrans)
		output = agequals.apply(fn, axis=1)
		output.to_csv(out_55pluspanel, index=False)
		'''