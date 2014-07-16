"""
This code merges the Beale Urbanicity variable (newbeale8511)
to PSID data by year and output as csv files.
"""
import pandas as pd 

# Set years to merge for 
years = range(1991,1998) + range(1997,2013,2)

# Set paths to Beale data, variable names, yearly data, and output file
fbeale = 'M:/Senior Living/Data/PSID Data/Beale Urbanicity/newbeale8511.csv'
fvars = 'M:/Senior Living/Data/PSID Data/agecohort_vars.csv'
fdata = 'M:/Senior Living/Data/PSID Data/years/' 
foutput = 'M:/Senior Living/Data/PSID Data/Merged Metro/'

def mergeBeale(y, fbeale, fvars, fdata, foutput): 

	# Beale data into df 
	beale = pd.read_csv(fbeale)

	# Yearly data into df 
	famintnum = (pd.read_csv(fvars).groupby('year').get_group(y)).reset_index().loc[0, 'famintnum']
	ydf = pd.read_csv(fdata+str(y)+'.csv').dropna(subset=[famintnum])

	# Isolate yearly obs from Beale df
	yBeale = pd.DataFrame(beale.loc[beale['CBV2'] == y])

	# Merge yearly obs to yearly data by fam id
	yBeale.rename(columns = {'CBV3': famintnum}, inplace = True)
	output = pd.merge(ydf, yBeale, how = 'outer')

	# Outsheet 
	output.to_csv(foutput+str(y)+'.csv', index=False)

if __name__ == '__main__': 
	for y in years: 
		print "Writing for " + str(y)
		mergeBeale(y, fbeale, fvars, fdata, foutput)
