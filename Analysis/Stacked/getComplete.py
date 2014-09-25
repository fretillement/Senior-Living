from getStackedFrame import *
from fillMissing import *
from identifyHousing import *
import pandas as pd



'''
This script does the following:

1. Constructs a simple person-year stacked dataframe from the most RECENT
PSID raw data set with the vars in varlist below

2. Fills in missing age and moved values for people present in the survey

3. Marks current housing type, transitions, and transition structures

4. Writes the resulting dataframe to a csv (outputfile). 

It uses the getStackedFrame, fillMissing, and identifyHousing modules. 
'''
# Edit most recent PSID file below
mostrecent = "J178305" 

# Edit the output file below
fpath_output = "M:/test.csv"

# Edit the varlist below
varlist = ['hstructure', 'htenure', 'moved', 'indweight', 'numrooms', \
			'seniorh', 't_seniorh', 'relhead', 'whymoved', 'tinst', \
			'income', 'race', 'gender', 'mar', 'educ', 'obstype', 'impwealth', 'health']

# Create a simple stacked dataframe using the MOST RECENT
# PSID raw data and varlist below
print "Construct simple person-year stacked df"
complete = getStackedFrame('age', mostrecent).implement()
for v in varlist: 
	print "		"+v
	temp = getStackedFrame(v, mostrecent).implement()
	complete = complete.merge(temp, right_index=True, left_index=True, how='outer')
complete.to_csv("M:/test.csv")

# Fill in age and moved values for present individuals 
print "Fill in age and moved values for present individuals"
complete = complete.reset_index()
complete = complete.rename(columns={'level_1': 'year'})
complete = complete.groupby('unique_pid').apply(implementFill)
complete = complete.reset_index()
complete.to_csv("M:/test.csv", index=False)

# Identify transition types
print "Identify housing transitions"
complete = pd.read_csv("M:/test.csv")
complete = identifyHousing(complete)
complete = complete.implement()

# Write to a csv file 
print "Writing"
complete.to_csv(fpath_output, index=False)