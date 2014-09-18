from __future__ import division
import pandas as pd
from count_transitions import fillAges, calcSandwichAges, calcOutsideAges
import gc

# Set file paths: variable codes and raw data 
var_file = 'M:/Senior Living/Code/Senior-Living/Psid_clean/agecohort_vars.csv'
raw_file = 'M:/Senior Living/Data/PSID Data/J178148_edits.csv'
beale_fpath = 'M:/Senior Living/Data/Psid Data/Beale Urbanicity/NewBeale8511.csv'

# Set namestub list 
ids_list = ['id1968', 'personnum', 'age']
vars_list = ['hstructure', 'htenure', 'moved', 'indweight', 'numrooms', \
			'seniorh', 't_seniorh', 'relhead', 'whymoved', 'tinst', 'famid', \
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


# Get codes of age, moved, hstructure, tenure and id variables 
def getCodes(namestub, varfile=var_file): 
	values = pd.read_csv(varfile, usecols = [namestub, 'year']).dropna()
	years = map(int, values['year'].tolist())
	codes = values[namestub].tolist()
	#print years,codes
	return [years, codes]

def readRaw(rawfile=raw_file, varfile=var_file, namestub_list=namestub_list): 
	ages = getCodes('age')[1]
	cols = ages
	for n in namestub_list: 
		cols = getCodes(n)[1] + cols
	raw = pd.read_csv(rawfile)
	# Keep only obs >= 25 at any given point 
	for n in ages: 
		if n not in raw.columns.tolist(): print n
	raw['25plus'] = (raw.loc[:, ages] >= 25).sum(axis=1) > 0 
	return raw

def getSepFrames(namestub): 
	raw = readRaw()
	codes = list(set(getCodes(namestub)[1]))
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

#print "Constructing basic vars"
#codes = getCodes('gender')[1]
#df = readRaw()
#for c in codes: 
#	if c not in df.columns.tolist(): print c
#stackdf('gender')

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
		return row

def markShared(df): 
	df['Housing Category'] = 0
	pre83_mask = ((df['year'] < 1983))
	post83_mask = ((df['year'] >= 1983))
	shared_mask = ((pre83_mask & (~df['relhead'].isin([0,1,2,8]))) | (post83_mask & (~df['relhead'].isin([0,10,20,90]))))
	df.loc[shared_mask, 'Housing Category'] = 'Shared'
	return df 

def markSFO(df): 
	df = markShared(df)
	sf_mask = ((df['hstructure'] == 'Single-family house'))
	owner_mask = ((df['htenure'] == 1))
	renter_mask = ((df['htenure'] == 5))
	notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
	sfo_mask =  ((sf_mask & owner_mask & notshared_mask) | (sf_mask & renter_mask & notshared_mask))
	df.loc[sfo_mask, 'Housing Category'] = 'SFO/ SFR'
	return df

def markMFR(df):
 	df = markSFO(df)
 	notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
 	mf_mask = ((df['hstructure'].isin(['Duplex/ 2-family house', 'Multifamily',\
 				'Townhouse', 'Other'])))
 	#renter_mask = ((df['htenure'].isin([5])))
 	#owner_mask = ((df['htenure'].isin([1])))
 	mfr_mask = ((mf_mask & notshared_mask))
 	df.loc[mfr_mask, 'Housing Category'] = 'MFR/ MFO'
 	return df

def markSeniorHousing(df): 
 	df = markMFR(df)
 	notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
 	seniorh_mask = (((df['seniorh'].isin([1]) | (df['inst'].isin([1]))) & notshared_mask)) 
 	df.loc[seniorh_mask, 'Housing Category'] = 'Senior housing'
 	return df

def markHousingTo(df):
	df = markSeniorHousing(df) 
	df['Trans_to'] = 0
	moved_mask = (df['moved']==1)
	df.loc[moved_mask, 'Trans_to'] = df['Housing Category']
	return df

def markHousingFrom(df):
	df = markHousingTo(df) 
	grouped = df.groupby('unique_pid')
	def getFrom(gr): 
		gr['Trans_from'] = 0
		if gr.loc[(gr['moved']==1), 'moved'].sum() > 0: 
			gr_iter = gr.iterrows()
			for l in gr_iter: 
				(index, line) = l
				if line['moved'] == 1 and index-1 in gr.index: gr.loc[index, 'Trans_from'] = gr.loc[index-1, 'Housing Category']		
		return gr 
	df = grouped.apply(getFrom)
	return df

def mergeBeale(df, beale_fpath=beale_fpath):
	df['urbancode'] = 0
	bealedf = pd.read_csv(beale_fpath).groupby(['CBV2', 'CBV3'])
	for group in bealedf: 
		(key, g) = group
		(year, famid) = key
		id_mask = ((df['year']==year) & (df['famid']==famid))
		df.loc[id_mask, 'urbancode'] = g['CBV4'].iloc[0]
		print key
	return df 

print "Stacking all variables into one df"
age = stackdf('age')
for n in vars_list: 
	print n
	age = age.merge(stackdf(n), right_index=True, left_index=True, how='outer')
print age.columns.tolist()
age.to_csv("M:/senior living/data/psid data/basicvars.csv")

print "Fill-in procedure for age and moved vars"
df = pd.read_csv("M:/senior living/data/psid data/basicvars.csv")
df = df.rename(columns={'Unnamed: 1': 'year'})
df_ages = df.groupby('unique_pid').apply(fillMissingMoved)
print "**Writing**"
df_ages.to_csv("M:/senior living/data/psid data/basicvars_age.csv")

print "Renaming/ marking housing categories"
df = pd.read_csv("M:/senior living/data/psid data/basicvars_age.csv")
print "		Identifying institutionalization"
df = anyInst(df)
df = df.apply(renameHstructure, axis=1)
print "  	Marking housing transition categories"
df = markHousingFrom(df)
print "		**Writing**"
df.to_csv("M:/senior living/data/psid data/allvars_st.csv", index=False)




def ageTrans(df): 
	df_gr = df.groupby('age2')
	
	def ageGrCount(gr): 
		age = gr['age2'].iloc[0]
		output = {age: {}}
		existingcat = gr['Housing Category'].value_counts()
		tocat = gr['Trans_to'].value_counts()
		fromcat = gr['Trans_from'].value_counts()
		numtrans = len(gr.loc[((gr['moved']==1) & (gr['Housing Category'] != 0))].index)
		for c in existingcat.index: 
			info = {c: existingcat[c]}
			output[age].update(info)
		for c in tocat.index:
			#print c
			#info = {'to_'+str(c): tocat[c]/numtrans}
			info = {'to_'+str(c): tocat[c]}
			output[age].update(info)
		for c in fromcat.index: 
			#info = {'from_'+str(c): fromcat[c]/numtrans}
			info = {'from_'+str(c): fromcat[c]}
			output[age].update(info)	
		return pd.DataFrame.from_dict(output, orient='index') 

	sharesdf = df_gr.apply(ageGrCount)
	return sharesdf

#df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
#df = df.rename(columns={'housingcategory': 'Housing Category'})
#df = mergeBeale(df)
#print "Writing"
#df.to_csv('M:/senior living/data/psid data/allvars_st_urban.csv')
'''
df = pd.read_csv('M:/senior living/data/psid data/allvars_st_urban.csv')

urbancode_mask = ((df['urbancode'] <= 6) & (df['urbancode'] >= 1)) 
ruralcode_mask = ((df['urbancode'] >= 7)) 

urbandf = df.loc[urbancode_mask]
ruraldf = df.loc[ruralcode_mask]

#range(1968, 1985), 
ranges = [range(1985, 1996), range(1996, 2000) + range(1999, 2013, 2)]
for timespan in ranges: 
	urban_timeobs = urbandf.loc[((urbandf['year'].isin(timespan))), :] 
	rural_timeobs = ruraldf.loc[((ruraldf['year'].isin(timespan))), :] 

	urbandf_shares = ageTrans(urban_timeobs)
	ruraldf_shares = ageTrans(rural_timeobs)

	name = str(min(timespan)) + '-' + str(max(timespan))
	print name 

	urbandf_shares.to_csv("M:/senior living/data/psid data/hcatnums_urban_"+name+".csv", index=True)
	ruraldf_shares.to_csv("M:/senior living/data/psid data/hcatnums_rural_"+name+".csv", index=True)


#df_shares = ageTrans(df)
#df_shares.to_csv("M:/senior living/data/psid data/housingcat_nums.csv", index=True)

'''