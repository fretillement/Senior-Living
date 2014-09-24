from __future__ import division
import pandas as pd
#from count_transitions import fillAges, calcSandwichAges, calcOutsideAges
import gc

class getStackedFrame: 
	'''
	A class of functions to generate a stacked dataframe with a variable (namestub)
	and id variables (ER30001, ER30002, 'unique_pid')
	'''
	# Set namestub list 
	ids_list = ['id1968', 'personnum', 'age']
	vars_list = ['hstructure', 'htenure', 'moved', 'indweight', 'numrooms', \
			'seniorh', 't_seniorh', 'relhead', 'whymoved', 'tinst', \
			'income', 'race', 'gender', 'mar', 'educ', 'obstype', 'wealth', \
			'impwealth', 'health']
	namestub_list = ids_list + vars_list

	#Set possible hstructure cats
	hstruct_dict = {1.0: 'Single-family house', 
			 2.0: 'Duplex/ 2-family house', 
			 3.0: 'Multifamily', 
			 4.0: 'Mobile Home/ trailer', 
			 5.0: 'Condo', 
			 6.0: 'Townhouse', 
			 7.0: 'Other', 
			 8.0: "Don't know", 
			 9.0: "Refused" 
			 }

	def __init__(self, namestub, mostrecent): 
		self.mostrecent = mostrecent
		self.namestub = namestub
		self.rawfile = 'M:/Senior Living/Data/PSID Data/' + self.mostrecent + '.csv'
		#self.rawfile = '/users/shruthivenkatesh/desktop/senior-living-proj/data/' + self.mostrecent + '.csv'

	# Set file paths: variable codes and raw data 
	var_file = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
	#var_file = '/users/shruthivenkatesh/desktop/senior-living-proj/Psid_clean/agecohort_vars.csv'
	beale_fpath = 'M:/Senior Living/Data/Psid Data/Beale Urbanicity/NewBeale8511.csv'
	basicvars_fpath = "M:/senior living/data/psid data/basicvars.csv"
	#basicvars_fpath = "/users/shruthivenkatesh/desktop/senior-living-proj/data/basicvars.csv"
	basicvars_age_fpath = "M:/senior living/data/psid data/basicvars_age.csv"
	#basicvars_age_fpath = "/users/shruthivenkatesh/desktop/senior-living-proj/data/basicvars_age.csv"
	
		
	# Get codes of age, moved, hstructure, tenure and id variables 
	def getCodes(self, varfile=var_file): 
		values = pd.read_csv(varfile, usecols = [self.namestub, 'year']).dropna()
		years = map(int, values['year'].tolist())
		codes = values[self.namestub].tolist()
		#print years,codes
		return [years, codes]

	def readRaw(self, varfile=var_file):
		mostrecent = self.mostrecent 
		ages = getStackedFrame('age', mostrecent).getCodes()[1]
		n = self.namestub
		cols = getStackedFrame(n, mostrecent).getCodes()[1] 
		id1968 = getStackedFrame('id1968', mostrecent)
		personnum = getStackedFrame('personnum', mostrecent)
		ids = list(set(id1968.getCodes()[1])) + list(set(personnum.getCodes()[1]))
		raw = pd.read_csv(self.rawfile, usecols=cols+ages+ids)
		raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 
		raw = raw.loc[raw['25plus']>0, cols+ids]
		return raw

	def genUniqueID(self): 
		sep = self.readRaw()
		sep['unique_pid'] = sep['ER30001'].map(str)+ "_" + sep['ER30002'].map(str)
		sep = sep.drop(['ER30001', 'ER30002'], axis=1)
		(years, codes) = self.getCodes()
		sep = sep.rename(columns= dict(zip(codes, years)))
		return sep 

	def stackdf(self): 
		sep = self.genUniqueID()
		st_sep = pd.DataFrame(sep.set_index('unique_pid').stack())
		st_sep = st_sep.rename(columns={0:self.namestub, 'level_1':'year', 'Unnamed: 1': 'year'})
		return st_sep


if __name__ == "__main__":
	'''
	Edit to point to the most recent raw file
	'''
	mostrecent = "J178305"
	age = getStackedFrame('numrooms', mostrecent)
	print age.stackdf()