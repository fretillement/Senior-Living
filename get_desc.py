import csv
import pandas as pd 

''' 
This program should generate a csv of all the variables in the updated PSID file J174506.txt 
organized by category and year.  
''' 

# Read description master file into a dataframe 
df = pd.read_csv('M:/Senior Living/Data/PSID Data/All_weights/J174506_desc_withyear.csv')

# Group dataframe by year 
grouped = df.groupby('year')

# Initialize a dict of lists with years as keys 
vardict = {y: [] for y in range(1968,2012)}
namesdict = {y: [] for y in range(1968, 2012)}

# Iterate through each year group and append to dict 
for g in grouped: 
	(year, data) = g 
	vardict[year] = vardict[year] + list(data['varlab'])
	namesdict[year] = namesdict[year] + list(data['name'])
nonempty = dict((k, v) for k,v in vardict.iteritems() if v) 
info = []
for t in nonempty: 
	info.append([t] + nonempty[t])
	info.append([t] + namesdict[t])
	
# Output to csv
output = csv.writer(open('M:/Senior Living/Data/PSID Data/All_weights/J174506_vars.csv', 'w'), lineterminator = '\n')
for i in info: 
	output.writerow(i)

