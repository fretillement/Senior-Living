import pandas as pd 
import os

''' 
This script counts and characterizes the housing 
transitions of the elderly in PSID file J170612 
'''
# Set filepaths
out = "M:/Senior Living/Data/PSID Data/Panel/transitions.csv"
panel_code = "M:/Senior Living/Code/Senior-living/Housing55/get_panel.py"
paneldata = "M:/Senior Living/Data/PSID Data/Panel/elderly_panel.csv"
vardata = "M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv"

# Extract info about elderly only 
#execfile(panel_code)

# Get years
years = map(str, range(1975, 1998) + range(1999, 2012, 2))
missing = map(str, [1973, 1974, 1982])

# Read panel and varlabel data  
df = pd.read_csv(paneldata)
vardf = pd.read_csv(vardata)
age_df = df.loc[:, ['unique_pid']+['age' + x for x in years]]


# Generate a total num_transitions var
def totalTransitions(df):
	transitions = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
	df['num_transitions'] = transitions.apply(lambda x: x.nunique()-1, axis=1)
	return df

# Generate dummy vars for each type of transition (1-9)
def countTransitions(df): 
	# Takes a df with housing structure vars and person id
	# Returns df with dummies for each type of transition entered

	# Stack obs in transition df by unique_pid 
	hstructure = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
	st = pd.DataFrame(hstructure.set_index('unique_pid').stack(), columns=['hstructure'])

	# Reset index for pivoting. Creates 'index' var and removes hierarchical indexing
	st.reset_index(inplace=True)
	st.reset_index(inplace=True)

	# Pivot the observations 
	piv = st.pivot(index='index', columns='hstructure', values='unique_pid')

	# Rename columns
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
	piv = piv.rename(columns=namesdict)

	# Convert the info in pivoted df to dummy vars
	piv['unique_pid'] = piv.max(axis=1, skipna=True)
	#piv.set_index('unique_pid', inplace=True, drop=True)
	piv.fillna(0, inplace=True)
	piv = piv.drop(labels=[0], axis=1)
	piv[piv.loc[:, namesdict.values()]>0] = 1
	
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

def fillAges(group): 
	group.reset_index(inplace=True)
	g = group['age']
	first = g[g>0].first_valid_index()
	last = g[g>0].last_valid_index()
	l = len(g.index)
	output = []
	if (first > 0) and (last+1 < l): print ["Odd solutions", first, last]
	'''
	if (last+1== l and first == 0):
		#print "1"
		output.append("equal")
		#out = pd.DataFrame(calcAges(group, g, first, last, l, 1))
		#group['age2'] = out
		#print '1'
		#return group
	#print [last, first, l]
	if (last+1 < l and first == 0):
		output.append("less than")
		#out = pd.DataFrame(calcAges(group, g, first, last, l, 2))
		#group['age2'] = out
	#	print "2"
		#return group
	if (last+1+first > l):
	#	print "3"
		output.append("greater than")
	#	#out = pd.DataFrame(calcAges(group, g, first, last, l, 3))
	#	#group['age2'] = out
	#	print '3'
		#return group
	#else: print [last+first < l]
	print output
	'''



def calcAges(group, g, first, last, l, condition): 	
	o = map(int, g[g>0].tolist())
	if condition == 1: 
		return o
	if condition == 2: 
		while (last+1 < l) :	
			#print group['unique_pid']
			thisyr = group.ix[last, 'year'] 
			nextyr = group.ix[last+1, 'year']
			#o.append(g.ix[last, 0]+(next-this))
			last = last + 1
			#print last
			#print g.ix[int(last),0]
		return o 
	if condition == 3:
		#print g.first_valid_index()
		while (first >= g.first_valid_index()) :
			#thisyr = int(group.ix[first, 'year'])
			#prevyr = int(group.ix[first-1, 'year'])
			#print [group.ix[first,'unique_pid'], g[first]-(thisyr-prevyr)]
			#o = [g[first]] + o
			#o.insert(0, int(g[int(first)]-(thisyr-prevyr)))
			first = first -1
			print [first in g.index.tolist()]
		return o
	else : 
		return "Error"





if __name__ == "__main__": 
	#tcounts = countTransitions(df)
	#fn = lambda x: ageLookup(x, age_df)
	#tcounts['age'] = tcounts.apply(fn, axis=1)
	#tcounts.set_index('unique_pid', inplace=True)
	#print tcounts.head(30)
	#tcounts.to_csv(out)
	#fillAges(out)
	df1 = pd.read_csv(out, usecols=['age', 'unique_pid', 'year'])
	df2 = df1.groupby('unique_pid').apply(fillAges)
	#df3 = df2.apply(fillAges)
	#print df1.head(30)