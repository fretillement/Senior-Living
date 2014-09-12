import pandas as pd
from count_transitions import fillAges, calcSandwichAges, calcOutsideAges
import gc

# Set file paths: variable codes and raw data 
var_file = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
raw_file = 'M:/Senior Living/Data/PSID Data/J177301.csv'

# Set namestub list 
ids_list = ['id1968', 'personnum', 'age']
vars_list = ['hstructure', 'htenure', 'moved', 'indweight', 'numrooms', \
			'seniorh', 't_seniorh', 'relhead', 'whymoved', 'tinst']
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


# Get codes of age, moved, hstructure, tenure and id variables 
def getCodes(namestub, varfile=var_file): 
	values = pd.read_csv(varfile, usecols = [namestub, 'year']).dropna()
	years = map(int, values['year'].tolist())
	codes = values[namestub].tolist()
	return [years, codes]

def readRaw(rawfile=raw_file, varfile=var_file, namestub_list=namestub_list): 
	cols = []
	for n in namestub_list: 
		cols = getCodes(n)[1] + cols
	raw = pd.read_csv(rawfile, usecols=cols)
	# Keep only obs >= 25 at any given point 
	ages = getCodes('age')[1]
	raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 
	return raw

def getSepFrames(namestub): 
	raw = readRaw()
	codes = getCodes(namestub)[1]
	ids = list(set(getCodes('id1968')[1])) + list(set(getCodes('personnum')[1]))
	sep = raw.loc[(raw['25plus'] > 0), codes + ids]
	return sep

def genUniqueID(namestub): 
	sep = getSepFrames(namestub)
	sep['unique_pid'] = sep['ER30001'].map(str)+ "_" + sep['ER30002'].map(str)
	sep = sep.drop(['ER30001', 'ER30002'], axis=1)
	(years, codes) = getCodes(namestub)
	sep = sep.rename(columns= dict(zip(codes, years)))
	return sep 

def stackdf(namestub): 
	sep = genUniqueID(namestub)
	st_sep = pd.DataFrame(sep.set_index('unique_pid').stack())
	st_sep = st_sep.rename(columns={0:namestub, 'level_1':'year', 'Unnamed: 1': 'year'})
	return st_sep

# Identify "sandwich rows" and strip all rows 
# that are not part of a "sandwich" and have BOTH 'age'
# and 'moved' values equal to 0
def getMissingAges(gr): 
	print gr['unique_pid'].iloc[0]
	gr = gr.fillna(0)
	if 999 in gr['age'].tolist(): 
		gr.loc[(gr['age'] == 999), 'age'] = 0
	gr = gr.reset_index()
	trailing_mask = ((gr['age'] > 0) | ((gr.loc[:, vars_list]).sum(axis=1) > 0))
	#print gr.loc[trailing_mask,['age', 'moved']]
	if gr.loc[trailing_mask,['age', 'moved']].empty :
		return gr.loc[trailing_mask,:]
	else:
		first = gr.loc[trailing_mask,['age', 'moved']].first_valid_index()
		last = gr.loc[trailing_mask, ['age', 'moved']].last_valid_index()
		gr = gr.loc[(gr.index >= first) & (gr.index <= last), :]
		sandwich_mask = ((gr['age'].cumsum() > 0) & (gr['moved'].cumsum()>0)
			    & (gr['age'] == 0) & (gr['moved'] == 0))
		gr.loc[sandwich_mask, ['age', 'moved']] = 0
		return gr	

# Fill in ages using fillAges function from count_observations
def fillMissingAges(gr): 
	gr = getMissingAges(gr)	
	if gr.empty: 
		return gr
	else: 
		gr = fillAges(gr)
		return gr 		

# Fill in missing "moved" observations (if at least one other var exists)
def fillMissingMoved(gr): 
	print gr['unique_pid'].iloc[0]
	gr = fillMissingAges(gr)
	if gr.empty: 
		return gr
	else: 	
		gr['moved2'] = gr.loc[:, 'moved']
		missing_move = ((gr['moved'] == 0) & (gr.loc[:, vars_list].sum(axis=1) > 0))
		gr.loc[missing_move, 'moved2'] = 5
		gr = gr.loc[(gr['age2']>0), :]
		return gr

# Identify members of the panel who have been institutionalized
# Based on method outlined in Ellwood and Kane (1990)
def anyInst(df): 
	df['inst'] = 0
	ek1990_inst_mask = ((df['moved'] == 1) & (df['whymoved'] == 7) \
				&  (df['numrooms'] <= 2) & (df['hstructure'] == 7))
	seniorh_mask = (df['seniorh'] == 1)
	instvar_mask = ((df['tinst'] == 3) | (df['tinst'] == 7))
	df.loc[ek1990_inst_mask | seniorh_mask | instvar_mask, 'inst'] = 1 
	return df 

def renameHstructure(row, hstruct_dict=hstruct_dict): 
	if row.loc['hstructure'] == 0: return row 
	else: 
		row.loc['hstructure'] = hstruct_dict[row.loc['hstructure']]
		row.loc['movedto'] = row.loc['hstructure']
		return row

def markShared(df): 
	df['Housing Category'] = 0
	pre83_mask = ((df['year'] < 1983))
	post83_mask = ((df['year'] >= 1983))
	shared_mask = ((pre83_mask & (~df['relhead'].isin([1,2,8]))) | (post83_mask & (~df['relhead'].isin([10,20,90]))))
	df.loc[shared_mask, 'Housing Category'] = 'Shared'
	return df 

def markSFO(df): 
	df = markShared(df)
	sf_mask = ((df['hstructure'].isin([1])))
	owner_mask = ((df['htenure'].isin([1])))
	notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
	sfo_mask =  ((sf_mask & owner_mask & notshared_mask))
	df.loc[sfo_mask, 'Housing Category'] = 'SFO'
	return df

def markMFR(df):
 	df = markSFO(df)
 	notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
 	mf_mask = ((df['hstructure'].isin([2, 3, 6, 7])))
 	renter_mask = ((df['htenure'].isin([5])))
 	mfr_mask = ((mf_mask & renter_mask & notshared_mask))
 	df.loc[mfr_mask, 'Housing Category'] = 'MFR'
 	return df

def markSeniorHousing(df): 
 	df = markMFR(df)
 	#notshared_mask = ((~df['Housing Category'].isin(['Shared']))
 	seniorh_mask = ((df['seniorh'].isin([1]) | (df['inst'].isin([1])))) 
 	df.loc[seniorh_mask, 'Housing Category'] = 'Senior housing'
 	return df

df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
df = markSeniorHousing(df)
print "Writing"
df.to_csv("M:/senior living/data/psid data/housingcat_st.csv")

'''














#output = gr_merged.apply(fillMissingMoved)
#print "**Writing**"
#output.to_csv("M:/Senior living/data/psid data/edited_vars_68-75.csv")
#output.to_csv("/users/shruthivenkatesh/desktop/senior-living-proj/data/edited_vars.csv")
#print fixMissing(test)
#test= fillMissingAges(test)
#print test.loc[:, ['age', 'age2', 'year', 'moved']]
#print fillMissingMoved(test)

gc.collect()

'''