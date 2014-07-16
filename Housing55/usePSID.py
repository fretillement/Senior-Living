import pandas as pd
import numpy as np

class usePSID:
	'''
	Common class of functions to manipulate any PSID yearly dataset
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

	# Isolate head obs
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
		agecat = pd.DataFrame(pd.cut(dfnew[agevar], 
			bins = nbins, 
			labels = False, 
			retbins = False), 
			columns = ['agecat'])
		return pd.merge(dfnew, agecat, 
			left_index = True, 
			right_index = True, 
			right_on = ['agecat'])

	# Compute weighted share of a group by values of varlab
	def computeShare(self, varlab, wtlab): 
		output = {}
		data = self.df
		select_var = self.getVarname(varlab)
		wt_var = self.getVarname(wtlab)
		for g in data.groupby(select_var): 
			(group, info) = g
			output[group] = np.true_divide(info[wt_var].sum(), info[wt_var].sum())
		return output 

'''
# Testing functions in cohortShare 
fname = 'M:/Senior Living/Data/PSID Data/Years/1991.csv'
year = 1991
vname = "M:/Senior Living/Data/PSID Data/Agecohort_vars.csv"

def testSuite(): 
	obj = cohortShare(year, fname, vname)
	#obj.getVars()
	#housing_var = obj.getVarname('htenure')
	#obj.headsOnly()
	#print obj.year
	#obj.select('htenure', 1)
	#obj.groupAge()
	#obj.mergeAgeCohort(125, 50, 8)
	#obj.computeShare('htenure', 'famwt')

if __name__ == "__main__": 
	testSuite()
'''