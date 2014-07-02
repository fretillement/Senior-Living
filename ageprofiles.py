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
	colind = []
	names = list(itertools.chain(*(cols.values())))
	for n in names: 
		if n in header: colind.append(header.index(n)) 
	df = read_csv(fpath, header = 0, usecols = colind) 
	return df

# Identify age cohorts; returned grouped df by age 
def ageCat(df, agevar, nbins): 
	# KEEP ONLY OBSERVATIONS WITH AGE VALUES
	dfnew = df.loc[(df[agevar] >= 50) &  (df[agevar] <= 125)]
	agecat = DataFrame(cut(dfnew[agevar], bins = nbins, labels = False, retbins = False), 
		columns = ['agecat'])
	output = merge(dfnew, agecat, left_index = True, right_index = True, right_on = ['agecat'])
	return output 

# For a given age group, calculate weighted share in each of housing, structure, and tenure type
def cohortProfile(df, var, weight, labelsdict, y): 
	agegroups = df.groupby('agecat')
	agedict = {}
	for g in agegroups: 
		(age, group) = g
		agedict[age] = share(group, var, weight, labelsdict, y)
	return agedict

def share(agegroupdf, var, weight, labelsdict, y): 
	output = {}
	if var in agegroupdf.columns: 
		vargrouped = agegroupdf.groupby(var)
		for g in vargrouped: 
			(cat, df) = g 
			output[str(labelsdict[cat])+'_'+str(y)] = np.true_divide(df[weight].sum(), agegroupdf[weight].sum())
	return output 


'''
Implement above functions 
'''
# Edit number of age buckets desired below
nbins = 7

# Get all variables of interest in a groupby object 
vars_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/agecohort_vars.csv'   
v_years = cohortVars(vars_fpath)

# Place all codes for each variable in dict
tenure_dict = {8: "Neither owns or rents", 9: "NA; Refused", 5: "Rents", 1: "Owns"}
structure_dict = {1: "One-family house", 2: "Two-family house", 3: "Apartment/housing project",
					4: "Mobile homes", 6: "Townhouse", 7: "Other", 9: "NA"}
seniorh_dict = {1: 'Yes', 5: 'No', 3: "Don't know", 8: "Don't know", 9:'NA', 0: "inap"}
tseniorh_dict = {1: 'Retirement community', 2: 'Senior citizen housing', 
					3: 'Nursing home', 4:'Home for the aged', 5: 'Adult foster care', 6: 'Assisted living', 
					8: "Don't know", 9: "NA", 0: "inap"}

# Initialize output dicts
pr_htenure = {t: {} for t in range(0, nbins+1)}
pr_hstructure = {t: {} for t in range(0, nbins+1)}
pr_seniorh = {t: {} for t in range(0, nbins+1)}
pr_tseniorh = {t: {} for t in range(0, nbins+1)}

years = range(1991, 1997) + range(1997, 2013, 2)
for y in years: 
	print y
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
	seniorh = v_years.get_group(y).reset_index().loc[0, 'seniorh']
	t_seniorh = v_years.get_group(y).reset_index().loc[0, 't_seniorh']

	# Generate categorical variables by age and attach to df 
	df_agecat = ageCat(yearlydf, agevar, nbins)

	# Get age profile for each variable of interest 
	tenure_prof = cohortProfile(df_agecat, htenure, indwt, tenure_dict, y)
	hstructure_prof = cohortProfile(df_agecat, hstructure, indwt, structure_dict, y)
	seniorh_prof = cohortProfile(df_agecat, seniorh, indwt, seniorh_dict, y)
	tseniorh_prof = cohortProfile(df_agecat, t_seniorh, indwt, tseniorh_dict, y)

	for k in tenure_prof:
		pr_htenure[k].update(tenure_prof[k])

	for k in hstructure_prof: 
		pr_hstructure[k].update(hstructure_prof[k])

	for k in seniorh_prof: 
		pr_seniorh[k].update(seniorh_prof[k])

	for k in tseniorh_prof: 
		pr_tseniorh[k].update(tseniorh_prof[k])

# Output to csv 
(DataFrame.from_dict(pr_htenure, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/htenure50.csv')
(DataFrame.from_dict(pr_hstructure, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/hstructure50.csv')
(DataFrame.from_dict(pr_seniorh, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/seniorh50.csv')
(DataFrame.from_dict(pr_tseniorh, orient = 'index')).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/type_seniorh50.csv')