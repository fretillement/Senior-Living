import pandas as pd
import numpy as np

class usePSID:
	'''
	A class of common functions to manipulate any PSID yearly dataset
	'''
	def __init__(self, year, fname, vname): 
		self.year = year 
		self.location = fname
		self.varloc = vname
		self.df = pd.read_csv(fname)

	# Get list of important variables for that year
	def getVars(self):
		vname = self.varloc
		y = self.year
		return pd.read_csv(vname).groupby('year').get_group(y).reset_index()

	# Get varname for a given label in that year 
	def getVarname(self, label):
		varlist = self.getVars()
		return varlist.loc[0, label]

	# Isolate household head obs
	def headsOnly(self):
		data = self.df 
		seqnum_var = self.getVarname('seqnum')
		relhead_var = self.getVarname('relhead')
		if (seqnum_var in data.columns) and (relhead_var in data.columns): 
			return data.loc[(data[seqnum_var] == 1) & (data[relhead_var] == 10)]			
		else: return data

	# Extract obs that answer 'trueval' to some question ('label')
	def select(self, label, trueval): 
		data = self.df
		select_var = self.getVarname(label)
		if select_var in data.columns: return data.loc[(data[select_var] == trueval)]
		else: return data 

	# Group the df by age 
	def groupAge(self):
		data = self.df
		age_var = self.getVarname('age')
		return data.groupby(age_var)

	# Merge a categorical age var to the df
	def mergeAgeCohort(self, upper, lower, nbins):
		data = self.df 
		agevar = self.getVarname('age')
		dfnew = data.loc[(data[agevar] >= lower) &  (data[agevar] <= upper)]
		agecat = pd.cut(dfnew[agevar], 
			bins = nbins, 
			labels = False) 
		df_agecat = pd.DataFrame(agecat, columns = ['agecat'])
		return pd.merge(dfnew, df_agecat, 
			left_index = True, 
			right_index = True, 
			right_on = ['agecat'])

	def getCodes(self, varlabel):
		if varlabel == 'htenure': return {8: "Neither owns or rents", 9: "NA; Refused", 5: "Rents", 1: "Owns"}
		if varlabel == 'hstructure': return {1: "One-family house", 2: "Two-family house", 3: "Apartment/housing project",
							4: "Mobile homes", 6: "Townhouse", 7: "Other", 9: "NA"}
		if varlabel == 'seniorh': return {1: 'Yes', 5: 'No', 3: "Don't know", 8: "Don't know", 9:'NA', 0: "inap"}
		if varlabel == 't_seniorh': return {1: 'Retirement community', 2: 'Senior citizen housing', 
							3: 'Nursing home', 4:'Home for the aged', 5: 'Adult foster care', 6: 'Assisted living', 
							8: "Don't know", 9: "NA", 0: "inap"}
		else: return 'Varlabel not found'

	# Compute weighted share of a group by values of varlab
	def computeShare(self, dfgr, varlab, wtlab): 
		output = {}
		data = self.df
		select_var = self.getVarname(varlab)
		wt_var = self.getVarname(wtlab)
		codes = self.getCodes(varlab)
		if select_var in dfgr.columns: 
			for g in dfgr.groupby(select_var): 
				(group, info) = g
				output[str(self.year)+'_'+codes[group]] = np.true_divide(info[wt_var].sum(), dfgr[wt_var].sum())
		return output 

	# Merge the Beale Urbanicity variable to a yearly df object
	def mergeBeale(self, fbeale): 
		beale = pd.read_csv(fbeale)
		y_beale = pd.DataFrame(beale.loc[beale['CBV2'] == self.year])
		famintnum = self.getVarname('famintnum')
		data = (self.df).dropna(subset=[famintnum])
		yBeale.rename(columns = {'CBV3': famintnum}, inplace = True)
		return pd.merge(ydf, yBeale, how = 'outer')

# Testing functions in cohortShare 
years = range(1991, 1997) + range(1997, 2013, 2)
nbins = range(50, 100, 5)
varlabel = "t_seniorh"
f_output = "M:/Senior Living/Data/PSID Data/Age Profiles/" + varlabel + ".csv"
vname = "M:/Senior Living/Data/PSID Data/Agecohort_vars.csv"

def testSuite(y, nbins, varlabel): 
	output = {i:{} for i in nbins[0:len(nbins)-1]}
	fname = 'M:/Senior Living/Data/PSID Data/Years/' + str(y) + '.csv'
	obj = usePSID(y, fname, vname)
	# Create an age indicator 
	df_age = obj.mergeAgeCohort(max(nbins), min(nbins), nbins)
	# Group by the age indicator 
	df_age_gr = df_age.groupby('agecat')
	# For each group, compute share of housing tenure/ type/ etc
	for g in df_age_gr: 
		(agegr, info) = g
		output[nbins[int(agegr)]].update(obj.computeShare(info, varlabel, 'indweight'))
	return output 

if __name__ == "__main__": 
	output = {i:{} for i in nbins[0:len(nbins)-1]}
	for y in years: 
		yearlyinfo = testSuite(y, nbins, varlabel)
		[output[i].update(yearlyinfo[i]) for i in yearlyinfo]
		print y
	(pd.DataFrame(output)).to_csv(f_output)