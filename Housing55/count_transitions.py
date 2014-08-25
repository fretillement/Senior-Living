import pandas as pd 
import os

''' 
This script counts the housing transitions of the elderly in PSID file J170612 
'''

# Set filepaths
#out = "M:/Senior Living/Data/PSID Data/Panel/transitions.csv"
out = "/Users/ShruthiVenkatesh/Desktop/transitions.csv"
panel_code = "M:/Senior Living/Code/Senior-living/Housing55/get_panel.py"
paneldata ="/users/ShruthiVenkatesh/Desktop/elderly_panel.csv"
#paneldata = "M:/Senior Living/Data/PSID Data/Panel/elderly_panel.csv"
vardata = "M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv"


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


# Get years
years = map(str, range(1975, 1998) + range(1999, 2012, 2))
missing = map(str, [1973, 1974, 1982])


# Read panel and varlabel data  
df = pd.read_csv(paneldata)
#vardf = pd.read_csv(vardata)
age_df = df.loc[:, ['unique_pid']+['age' + x for x in years]]


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
	hstructure = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
	st = pd.DataFrame(hstructure.set_index('unique_pid').stack(), columns=['hstructure'])

	# Reset index for pivoting. Creates 'index' var and removes hierarchical indexing
	st.reset_index(inplace=True)
	st.reset_index(inplace=True)

	# Pivot the observations 
	piv = st.pivot(index='index', columns='hstructure', values='unique_pid')

	# Rename the columns
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


if __name__ == "__main__": 
	tcounts = countTransitions(df, namesdict)
	fn = lambda x: ageLookup(x, age_df)
	tcounts['age'] = tcounts.apply(fn, axis=1)
	tcounts.set_index('unique_pid', inplace=True, drop=False)
	df_output = tcounts.groupby('unique_pid').apply(fillAges)
	#df_output.drop('index', axis=1, inplace=True)
	df_output.to_csv('/users/ShruthiVenkatesh/Desktop/transitions2.csv', index=False, columns=['unique_pid', 'age', 'age2']+namesdict.values())
