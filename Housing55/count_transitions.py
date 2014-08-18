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
years = map(str, range(1975, 1998) + range(1999, 2012, 2))

# Read panel and varlabel data  
df = pd.read_csv(paneldata)
vardf = pd.read_csv(vardata)

# Generate a total num_transitions var
missing = map(str, [1973, 1974, 1982])
transitions = df.loc[:, ['hstructure'+ x for x in years if x not in missing]+['unique_pid']]
df['num_transitions'] = transitions.apply(lambda x: x.nunique()-1, axis=1)


# Count up type of transitions each type 
stacked = pd.DataFrame(transitions.set_index('unique_pid').stack(), columns=['struct_type'])
stacked.reset_index(inplace=True)
stacked.reset_index(inplace=True)
pivoted = stacked.pivot(index='index', columns='struct_type', values='unique_pid')
pivoted = pivoted.fillna(0)
pivoted['unique_pid'] = pivoted.max(axis=0, skipna=True)




'''

# Generate age of first transition var


# Generate age of second transition 

# Gen first transition var

# Gen second transition var 

# List possible types of transitions 
tlabels = {1: 'Single-family', \
		   2: "Duplex/ Two-family", \
		   3: "Multi-family", \
		   4: "Mobile home/ trailer", \
		   6: "Townhouse/ row house", \
		   7: "Other", \
		   8: "Don't know", \
		   9: "Refused, N/A"}

# Create dummies for transition into each possible housing type


# Look at age of transition for each transition dummy

# Generate a num_transitions var for each type of possible transition ou1tcome


# Outsheet 
df.to_csv(out)

'''