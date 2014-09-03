from __future__ import division
import matplotlib.pyplot as plt
import pandas as pd

''' 
This program conducts exploratory analysis of elderly 
transitions esp. to senior living facilities in the most 
recent raw PSID file (current file = J177301.txt)
'''

#Find the final transition of the panel df
def findFinal(row): 
	transvars = [x for x in row.index if 'trans' in x and 'age' not in x \
				and 'final' not in x and 'num' not in x]
	trans = row[transvars].loc[row[transvars] != "0"]
	translist = trans.index.tolist()
	final = translist[len(translist)-1]
	row = row.set_value('finaltrans', final)
	return row

# Find the age at final transition of the panel df
def findFinalAge(row): 
	row = findFinal(row)
	final = row['finaltrans']
	agelab = 'age_' + final
	#print final
	finalage = row[agelab]
	row = row.set_value('age_finaltrans', finalage)
	return row

# Find the difference between the first and second transition (if any)	
def calcFirstDiffs(df): 
	df['first_diff'] = df['age_trans2'] - df['age_trans1']
	df['first_diff'].loc[df['first_diff']<0] = 0
	return df

# Calculate the transition share across all years by age


if __name__ == "__main__":
	datestrings = ['75-84', '85-99', '01-11']
	#datestrings = ['75-84']
	for date in datestrings: 
		print "Processing file for years "+ date
		
		# Set filepaths
		f_panel =  "M:/Senior Living/Data/PSID Data/Panel/55plus_trans" + date + ".csv"

		# Read in datasets
		full = pd.read_csv(f_panel)
		'''
		# Find age of final transition; attach it as a variable
		# Output to csv
		full = full.apply(findFinalAge, axis=1)
		full.to_csv(f_panel, index=False)
	
		# Calculate difference between first and second transition
		# Attach it to panel df
		full = calcFirstDiffs(full)
		full.to_csv(f_panel, index=False)
		'''
