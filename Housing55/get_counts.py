from pandas import *
import itertools 

'''
This code should return the count in weights and number of observations
of people matching a criteria across any years in the PSID 
(file J174506.txt). 
'''

# Set year 
y = 1991

# Read in df for a given year 
ydata_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/' + str(y) + '.csv'
df = read_csv(ydata_fpath, header = 0) 

# Get list of correct variables for a given year
vars_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/agecohort_vars.csv'
v = read_csv(vars_fpath).groupby('year')

# Group by age group, housing type, tenure, etc. 
def group(df, var, vardf, year): 
	code = vardf.get_group(year)[var]
	gr = df.groupby(code)
	return gr

# Count the number of observations in each group
# MUST specify obs for observation-based  
def count(grdf, vardf, year, obs):
	if obs: c= len(grdf.index)
	else: c = grdf[vardf.get_group(year)['famwt']].sum()
	return c

# Place this number in a seperate dataframe

# Write to csv 

