from getStackedFrame import *
from fillMissing import *
from identifyHousing import *
import pandas as pd



'''
This script does the following:

1. Constructs a simple person-year stacked dataframe from the most RECENT
PSID raw data set with the vars in varlist below, and the beale urbanicty variable

2. Fills in missing age and moved values for people present in the survey

3. Marks current housing type, transitions, and transition structures

4. Writes the resulting dataframe to a csv (fpath_output). 

It uses the getStackedFrame, fillMissing, and identifyHousing modules. 
'''
# Edit most recent PSID file below
mostrecent = "J178730" 

# Edit the output file below
fpath_output = "M:/complete_st.csv"

# Edit the varlist below
varlist = ['famid', 'hstructure', 'htenure', 'moved', 'indweight', 'numrooms', \
			'seniorh', 't_seniorh', 'relhead', 'whymoved', 'tinst', \
			'race', 'gender', 'mar', 'educ', 'obstype', 'impwealth', 'health']


# Create a simple person-year stacked dataframe using the MOST RECENT
# PSID raw data and varlist below
# This complete stacked data frame includes the urban/rural variable
def mergeBeale(df):
	beale_df = pd.read_csv('M:/Senior Living/Data/PSID Data/Beale Urbanicity/newbeale8511.csv')
	#df = pd.read_csv('M:/complete_st.csv')
	data = df.drop(['Unnamed: 1', 'unique_pid.1'], axis=1)
	beale_df = beale_df.rename(columns={'CBV2':'year', 'CBV3':'famid', 'CBV4': 'urban-rural code'})
	# Group data by 'famid' and year 
	data_gr = data.groupby(['famid', 'year'])
	beale_gr = beale_df.groupby(['famid', 'year'])
	# Go through each famid-year group in the data and look up their urban code
	def lookup(group, beale_gr): 
		key = (group['famid'].iloc[0], group['year'].iloc[0])
		if (key[0] > 0) and (key[1] >= 1985): 
			code = beale_gr.get_group(key)
			group['urban-rural code'] = code['urban-rural code'].iloc[0]
		return group
	lookup_fn = lambda x: lookup(x, beale_gr)
	output = data_gr.apply(lookup_fn)
	return output

print "Construct simple person-year stacked df"
complete = getStackedFrame('age', mostrecent).implement()
for v in varlist: 
	print "		"+v
	temp = getStackedFrame(v, mostrecent).implement()
	complete = complete.merge(temp, right_index=True, left_index=True, how='outer')
complete = complete.rename(columns={0: 'year'})
complete = mergeBeale(complete)
complete.to_csv("M:/test.csv")

# Fill in age and moved values for present individuals 
print "Fill in age and moved values for present individuals"
complete = pd.read_csv("M:/test.csv")
if 'unique_pid' not in list(complete): complete = complete.reset_index()
print list(complete)
complete = complete.rename(columns={'level_1': 'year', 'Unnamed: 1': 'year'})
complete = complete.groupby('unique_pid').apply(implementFill)
if 'unique_pid' not in list(complete): complete = complete.reset_index()
complete.to_csv("M:/test.csv", index=True)

# Identify transition types
print "Identify housing transitions"
complete = pd.read_csv("M:/test.csv")
complete = identifyHousing(complete)
complete = complete.implement()

# Write to a csv file 
print "Writing"
complete.to_csv(fpath_output, index=False)