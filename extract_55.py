import csv
import pandas as pd 

'''
Want to know: where do people >= 55 years old live? 
Characterize with housing structure, tenure type, and household size. 
Extract variable names from description file; use stata to extract actual variables. 
'''


# Read in description file using csv 
desc = csv.DictReader(open('M:/Senior Living/Data/PSID Data/complete_PSID_desc.csv', 'r'))

# For each year, isolate variables in a dict 
years = [str(y) for y in range(1990, 2012) if y % 2 != 0] 
varsdict = {y: {} for y in years}
vnames = ['OWN/RENT', '# IN FU', 'AGE', 'TYPE INSTITUTION', 'LIVE IN ELDERLY', 'TYPE ELDERLY', 'TYPE DU', 'TYPE DWELLING UNIT', 'NUMBER IN FAMILY UNIT']
vlabels =['Tenure', 'HH size', 'Age', 'Type of institution', 'Senior housing', 'Type of senior housing', 'Structure type', 'Structure type', 'HH size']
labelsdict = dict(zip(vnames, vlabels))

for line in desc: 
	y = line['year']
	if y in years: 
		varlab = line['varlab']
		for l in labelsdict: 
			if l in varlab: 
				varsdict[y].update(dict(zip([labelsdict[l]], [line['name']])))

# Output to a csv file 
h = list(set(vlabels)) + ['Year']
output = csv.DictWriter(open('M:/Senior LIving/Data/PSID Data/selected_vars.csv', 'w'), fieldnames = h, lineterminator = '\n')
output.writerow(dict(zip(h,h)))
for v in varsdict: 
	info = varsdict[v]
	info.update(dict(zip(['Year'], [v])))
	output.writerow(info)


