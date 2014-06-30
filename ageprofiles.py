import pandas as pd
import csv 
import itertools 

'''
This program should construct the share of population by age living in each type of housing structure
across years 1991-2011 from the PSID (file J174506)
''' 
# Select year 
y = 1999 

# Get the variables you'd like from each year into a df groupedby years
def cohortVars(fpath): 
	v = pd.read_csv(fpath)
	v_years = v.groupby('year')
	return v_years 

# Get the header, read in the data
def getHeader(fpath): 
	f = open(fpath, 'r')
	header = (csv.DictReader(f)).fieldnames 
	f.close()
	return header 

def getData(fpath, header, v_years, y):
	cols = (v_years.get_group(y)).to_dict(outtype = 'list')
	del cols['year']
	names = list(itertools.chain(*(cols.values())))
	df = pd.read_csv(fpath, header = 0, usecols = [header.index(n) for n in names]) 
	return df

# Identify age cohorts; returned grouped df by age 
def ageCat(df, agevar, nbins): 
	# KEEP ONLY OBSERVATIONS WITH AGE VALUES
	dfnew = df.loc[(df[agevar] > 0) & (df[agevar] < 999)]
	agecat = pd.DataFrame(pd.cut(dfnew[agevar], bins = nbins, labels = False, retbins = False), 
		columns = ['agecat'])
	output = pd.merge(dfnew, agecat, left_index = True, right_index = True, right_on = ['agecat'])
	return output 

# Get variable that refers to age in a given year
def getAgeVar(df, v_years, y):
	for a in v_years.get_group(y)['age'].values:
		agevar = a
	return agevar

# For a given age group, calculate weighted share in each of housing, structure, and tenure type
def cohortProfile(groupdf, hvar, hstructure, htenure): 
	housingtype = groupdf.groupby(hvar)
	return profile

# Implement functions above 
vars_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/agecohort_vars.csv'
ydata_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/' + str(y) + '.csv'
df = getData(ydata_fpath, getHeader(ydata_fpath), cohortVars(vars_fpath), y)
#merged = ageCat(df, ageCohort(df, cohortVars(vars_fpath), y), 3)
#print merged.columns

#mdata_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/J174506.csv'