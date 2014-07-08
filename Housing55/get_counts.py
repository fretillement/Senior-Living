from pandas import *
import itertools 

'''
This code should return the count in weights and number of observations
of people matching a criteria across any years in the PSID 
(file J174506.txt). 
'''

# Set years
years = range(1991, 1997) + range(1997, 2013, 2)

# Group a df by age
def ageCat(df, agevar, nbins): 
	# KEEP ONLY OBSERVATIONS WITH AGE VALUES
	dfnew = df.loc[(df[agevar] >= 50) &  (df[agevar] <= 125)]
	agecat = DataFrame(cut(dfnew[agevar], bins = nbins, labels = False, retbins = False), 
		columns = ['agecat'])
	output = merge(dfnew, agecat, left_index = True, right_index = True, right_on = ['agecat'])
	return output 


tenure_dict = {8: "Neither owns or rents", 9: "NA; Refused", 5: "Rents", 1: "Owns"}
structure_dict = {1: "One-family house", 2: "Two-family house", 3: "Apartment/housing project",
					4: "Mobile homes", 6: "Townhouse", 7: "Other", 9: "NA"}
seniorh_dict = {1: 'Yes', 5: 'No', 3: "Don't know", 8: "Don't know", 9:'NA', 0: "inap"}
tseniorh_dict = {1: 'Retirement community', 2: 'Senior citizen housing', 
					3: 'Nursing home', 4:'Home for the aged', 5: 'Adult foster care', 6: 'Assisted living', 
					8: "Don't know", 9: "NA", 0: "inap"}


vars_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/agecohort_vars.csv'
v = read_csv(vars_fpath).groupby('year')

varlist = {'htenure': tenure_dict, 'hstructure': structure_dict, 'seniorh': seniorh_dict, 't_seniorh': tseniorh_dict }
nbins = 7

for k in varlist: 
	output = {a: {} for a in range(0, nbins)}
	for y in years:
		print (y,k)
		indwt = v.get_group(y).reset_index().loc[0, 'indweight']
		agevar = v.get_group(y).reset_index().loc[0,'age']
		var = v.get_group(y).reset_index().loc[0, k] 	
		ydata_fpath = 'M:/Senior Living/Data/PSID Data/all_weights/' + str(y) + '.csv'
		df = read_csv(ydata_fpath, header = 0) 
		data = ageCat(df, agevar, nbins).groupby('agecat')
		for d in data: 
			(age, info) = d
			if var in info.columns: 
				gr_var = info.groupby(var)
				[output[age].update({(varlist[k])[g[0]]+'_'+str(y): (g[1][indwt].sum())}) for g in gr_var]
				output[age].update({'Total_'+str(y): info[indwt].sum()})
			else: output[age].update({'Total_'+str(y): info[indwt].sum()})
	# Write to csv 
	(DataFrame.from_dict(output, orient = 'index').sort_index(axis = 1)).to_csv('M:/Senior Living/Data/PSID Data/all_weights/Age profiles/wtsum_' + k+'.csv')
