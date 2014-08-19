import pandas as pd 
import os

''' 
This program counts and characterizes the housing 
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
years = map(str, range(1975, 1989) + range(1999, 2012, 2))

# Read panel and varlabel data  
df = pd.read_csv(paneldata)
vardf = pd.read_csv(vardata)

# Generate a total num_transitions var
missing = map(str, [1973, 1974, 1982])
transitions = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
df['num_transitions'] = transitions.apply(lambda x: x.nunique()-1, axis=1)
ages = df.loc[:, ['age' + x for x in years if x not in missing] + ['unique_pid']]

# Generate dummy vars for each type of transition (1-9)
def countTransitions(transitions, ages): 
	# Takes a df with housing structure vars and person id
	# Returns df with dummies for each type of transition entered

	# Stack obs in transition df by unique_pid 
	st = pd.DataFrame(transitions.set_index('unique_pid').stack(), \
		columns=['hstructure'])

	# Reset index for pivoting. Creates 'index' var and removes hierarchical indexing
	st.reset_index(inplace=True)
	st.reset_index(inplace=True)

	# Pivot the observations 
	piv = st.pivot(index='index', columns='hstructure', values='unique_pid')

	# Convert the info in pivoted df to dummy vars
	piv['unique_pid'] = piv.max(axis=1, skipna=True)
	piv.set_index('unique_pid', inplace=True, drop=True)
	piv[piv>0] = 1
	piv.fillna(0, inplace=True)

	# Add a year variable
	gr = piv.groupby(piv.index)
	piv['year'] = gr.apply(lambda x: pd.Series(range(1975, 1975+len(x[1].index)), index=x[1].index))

	# Return
	return piv

def age(agedf):
	agest = pd.DataFrame(agedf.set_index('unique_pid').stack(), columns=['age'])	
	agest.reset_index(inplace=True)	
	agest.set_index('unique_pid', inplace=True)
	agest = agest.drop('level_1', axis=1)
	agest = agest[agest['age']>0]
	return agest

# Generate age of transition var 
#countTransitions(transitions)
age(ages)
'''

	agest = agest.drop(['level_1'], axis=1)	

	agest.set_index('unique_pid', drop=True)

	agest = agest[agest['age'] > 0]


	return agest

# Generate age of first transition var


# Generate age of second transition 



# List possible types of transitions 
tlabels = {1: 'Single-family', \
		   2: "Duplex/ Two-family", \
		   3: "Multi-family", \
		   4: "Mobile home/ trailer", \
		   6: "Townhouse/ row house", \
		   7: "Other", \
		   8: "Don't know", \
		   9: "Refused, N/A"}


# Look at age of transition for each transition dummy

# Generate a num_transitions var for each type of possible transition ou1tcome


# Outsheet 
df.to_csv(out)

'''