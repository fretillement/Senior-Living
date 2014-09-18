from __future__ import division
import pandas as pd 

'''
This script returns counts by housing categories of economic &
demographic characteristics of PSID panel members (file: J178148_edits.csv)
'''

# Rename variables accordingly 
def renameEduc(df): 
	# Education 
	hs_mask = ((df['educ'] >= 0) & (df['educ'] <= 12))
	somecollege_mask = ((df['educ'] > 12) & (df['educ'] < 16))
	col_mask = ((df['educ'] == 16))
	gradsch_mask = ((df['educ'] > 16))
	df.loc[hs_mask, 'educ'] = "High school or below"
	df.loc[somecollege_mask, 'educ'] = "Some college"
 	df.loc[col_mask, 'educ'] = "College grad"
 	df.loc[gradsch_mask, 'educ'] = "Grad school"
 	return df 

def renameRace(df):
	racedict = {1: 'White', \
				2: 'Black or African-American', \
				3: 'American Indian/ Alaskan Native', \
				4: 'Asian', \
				5: 'Native Hawaiian or Pacific Islander', \
				7: 'Other', \
				8: "Don't know", \
				9: "Refused"}
	for code in racedict: 
		df.loc[(df['race']==code), 'race'] = racedict[code]
	return df 

def renameMarital(df): 
	df.loc[(df['mar'] > 0), 'mar'] = "Married"
	df.loc[(df['mar'] == 0), 'mar'] = "Single"
	return df 

def renameGender(df): 
	df_gr = df.groupby('unique_pid')
	def recodeGender(group):
		#print group['unique_pid'].iloc[0] 
		gender = group.loc[(group['gender'] > 0), 'gender']		
		if gender == 1: group.loc[:, 'gender'] = 'Male' 
		if gender == 2: group.loc[:, 'gender'] = 'Female'
		return group
	output = df_gr.apply(recodeGender)
	return output


def getDemog(df, demvars=['gender', 'mar', 'race', 'educ']):
	#df = renameGender(renameMarital(renameRace(renameEduc(df))))
	#df = df.drop(['Unnamed: 1', 'index', 'unique_pid.1'], axis=1)
	df = pd.read_csv("M:/senior living/data/psid data/allvars_demo.csv")
	cats = ['Trans_to', 'Trans_from', 'Housing Category']
	for d in demvars: 
		for c in cats: 
			temp = df.groupby([d,c])['unique_pid'].count().reset_index()
			temp = temp.rename(columns={d: d, c: c, 0L: 'counts_'+c})
			temp = temp.pivot(d, c, 'counts_'+c)
			#temp = temp.drop(0, axis=1)
			temp = temp.rename(columns={x: x+"_"+c for x in temp.columns.tolist()})
			print temp
			#[d, c, c+'_count'] = temp.reset_index().columns
			#print temp.columns.tolist()
			#.pivot('gender', 'Housing Category', )
			#temp = df.groupby(d, c)
			#print temp


def getIncomeStats(df): 
	inc_yr_mask = ((df['income']>0) & (~df['year'].isin([1973, 1974, 1982])))
	incwt = df.loc[inc_yr_mask, ['indweight', 'income', 'year',\
	 'Housing Category', 'Trans_to', 'Trans_from']]
	incwt['weighted_income'] = incwt['income'] * incwt['indweight']
	
	mask = ((incwt['year']==1979))
	print incwt.loc[mask, 'Trans_to'].value_counts()

	# Get median for each direction 
	#med_transto = incwt.groupby(['year', 'Trans_to'])['income'].median().reset_index()

	#print med_transto.pivot('year', 'Trans_to', 'income').head(20)

	
	'''
	med_transfrom = incwt.groupby(['year', 'Trans_from'])['income'].median()
	med_current = incwt.groupby(['year', 'Housing Category'])['income'].median()
	

	# Get weighted average for each direction 
	wavg = lambda x: x['weighted_income'].sum() / x['indweight'].sum()
	avg_transto = incwt.groupby(['year', 'Trans_to']).apply(wavg)
	avg_transfrom = incwt.groupby(['year', 'Trans_from']).apply(wavg)
	avg_current = incwt.groupby(['year', 'Housing Category']).apply(wavg)


	#mean_transto = incwt.groupby(['year', 'Trans_to'])['weighted_income'].sum()
	#print med_transto.reset_index()
	'''



#def demCounts(df)

df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
getDemog(df)
#getIncomeStats(df)
#incwt = df.loc[df['income']>0, ['indweight', 'income', 'year']]
#print type(incwt.groupby('year')['income'].median())


#income('Trans_to', 'to', df)

#print (incwt['income']*incwt['indweight']).median()

#print df.loc[((df['income']>0) & (df['year']==2011) & (df['moved'] == 1) & (df['Trans_to'] =='SFO/ SFR')), 'income'].describe()
#print income('Trans_from', "From", df)