import pandas as pd 
import os

''' 
This program counts and characterizes the housing 
transitions of the elderly in PSID file J170612 
'''
# Get years
years = map(str, range(1968, 1998) + range(1999, 2012, 2))

# Extract info about elderly only 
#panel_code = "M:/Senior Living/Code/Senior-living/Housing55/get_panel.py"
#execfile(panel_code)

# Read panel data into df 
df = pd.read_csv("M:/Senior Living/Data/PSID Data/Panel/elderly_panel.csv")
vardf = pd.read_csv("M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv")

# Generate a num_transitions var
missing = map(str, [1973, 1974, 1982])
transitions = df.loc[:, ['hstructure'+ x for x in years if x not in missing]]

df['num_transitions'] = transitions.sum(axis=1)

# Generate a num_transitions var for each type of possible transition ou1tcome

# Count up 