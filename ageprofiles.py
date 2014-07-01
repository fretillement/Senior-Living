from pandas import * 
import numpy as np 
import csv 
import itertools 

'''
This program constructs the share of population by age living in each type of housing structure
across years 1991-2011 from the PSID (file J174506)
''' 
# Get the variables you'd like from each year into a df groupedby years
def cohortVars(fpath): 
	v = read_csv(fpath)
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
	df = read_csv(fpath, header = 0, usecols = [header.index(n) for n in names]) 
	return df

# Identify age cohorts; returned grouped df by age 
def ageCat(df, agevar, nbins): 
	# KEEP ONLY OBSERVATIONS WITH AGE VALUES
	dfnew = df.loc[(df[agevar] > 0) &  (df[agevar] < 999)]
	agecat = DataFrame(cut(dfnew[agevar], bins = nbins, labels = False, retbins = False), 
		columns = ['agecat'])
	output = merge(dfnew, agecat, left_index = True, right_index = True, right_on = ['agecat'])
	return output 

# For a given age group, calculate weighted share in each of housing, structure, and tenure type
def cohortProfile(df, var, weight, labelsdict): 
	agegroups = df.groupby('agecat')
	agedict = {}
	for g in agegroups: 
		(age, group) = g
		agedict[age] = share(group, var, weight, labelsdict)
	return agedict

def share(agegroupdf, var, weight, labelsdict): 
	vargrouped = agegroupdf.groupby(var)
	output = {}
	for g in vargrouped: 
		(cat, df) = g 
		output[labelsdict[cat]] = np.true_divide(df[weight].sum(), agegroupdf[weight].sum())
	return output 


'''
Implement above functions 
'''
# Edit number of age buckets desired below
nbins = 8

# Get all variables of interest in a groupby object 
vars_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/agecohort_vars.csv'   
v_years = cohortVars(vars_fpath)

#years = range(1991, 1997) + range(1997, 2013, 2)
years = [1991]
for y in years: 
	ydata_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/' + str(y) + '.csv'

	# Get header in PSID yearly file 
	header = getHeader(ydata_fpath)

	# Read in yearly PSID file
	yearlydf = getData(ydata_fpath, header, v_years, y)

	# Get the variables for year in interest 
	htenure = v_years.get_group(y).reset_index().loc[0, 'htenure']
	hstructure = v_years.get_group(y).reset_index().loc[0, 'hstructure']
	indwt = v_years.get_group(y).reset_index().loc[0, 'indweight']
	agevar = v_years.get_group(y).reset_index().loc[0, 'age']

	# Generate categorical variables by age and attach to df 
	df_agecat = ageCat(yearlydf, agevar, nbins)

	# Place all codes for each variable in dict
	tenure_dict = {8: "Neither owns or rents", 9: "NA; Refused", 5: "Rents", 1: "Owns"}
	structure_dict = {1: "One-family house", 2: "Two-family house", 3: "Apartment/housing project",
					4: "Mobile homes", 6: "Townhouse", 7: "Other", 9: "NA"}

	# Get age profile for each variable of interest 
	pr_htenure = cohortProfile(df_agecat, htenure, indwt, tenure_dict)
	pr_hstructure = cohortProfile(df_agecat, hstructure, indwt, structure_dict)

	# Output to csv 
	#(DataFrame.from_dict(pr_htenure, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/htenure_'+ str(y) + '.csv')
	#(DataFrame.from_dict(pr_hstructure, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/hstructure_' + str(y) + '.csv')
