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
				6: 'Mentions color other than black or white', \
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
	df = renameGender(renameMarital(renameRace(renameEduc(df))))
	df = df.drop(['Unnamed: 1', 'index', 'unique_pid.1'], axis=1)
	df.to_csv("M:/senior living/data/psid data/allvars_demo.csv")
	#df = pd.read_csv("M:/senior living/data/psid data/allvars_demo.csv")
	cats = ['Trans_to', 'Trans_from', 'Housing Category']
	for d in demvars: 
		output  = pd.DataFrame(index=df[d].value_counts().index.tolist())
		for c in cats: 
			df = df.loc[df[c] != '0', :] 
			temp = df.groupby([d,c])['unique_pid'].count().reset_index()
			temp = temp.rename(columns={d: d, c: c, 0L: 'counts_'+c})
			temp = temp.pivot(d, c, 'counts_'+c)
			temp = temp.rename(columns={x: c+"_"+x for x in temp.columns.tolist()})
			output = temp.merge(output, right_index=True, left_index=True)
		print "Writing for "+d
		output.to_csv("M:/senior living/data/psid data/demographics/"+ d + "_count.csv", index=True)


def getIncomeStats(df): 
	inc_yr_mask = ((df['income']>0) & (~df['year'].isin([1973, 1974, 1982])))
	df = df.loc[inc_yr_mask, ['indweight', 'income', 'year',\
	 'Housing Category', 'Trans_to', 'Trans_from', 'moved']]
	df['weighted_income'] = df['income'] * df['indweight']
	
	#print df.loc[(df['Trans_from'] != '0') & (df['year']==1975), 'Trans_from'].value_counts()
	print df.loc[(df['Trans_from'] != '0') & (df['year']==1975), 'Housing Category'].value_counts()

	# Calculate and write median to csv
	#med_output = calcMedian(df, 'Trans_to')
	#med_output = med_output.merge(calcMedian(df, 'Trans_from'), right_index=True, left_index=True)
	#med_output = med_output.merge(calcMedian(df, 'Housing Category'), right_index=True, left_index=True)
	#med_output.to_csv('M:/senior living/data/psid data/demographics/med_income.csv')
	
	# Calculate and write weighted avg to csv 
	#avg_output = calcWavg(df, 'Trans_to')
	#avg_output = avg_output.merge(calcWavg(df, 'Trans_from'), right_index=True, left_index=True)
	#avg_output = avg_output.merge(calcMedian(df, 'Housing Category'), right_index=True, left_index=True)
	#avg_output.to_csv('M:/senior living/data/psid data/demographics/avg_income.csv')
	


def calcWavg(df, direction): 
	wavg = lambda x: x['weighted_income'].sum() / x['indweight'].sum()
	incwt = df.loc[df[direction] != '0']
	avg = incwt.groupby(['year', direction]).apply(wavg)
	avg = avg.reset_index().pivot('year', direction, 0)
	avg = avg.rename(columns={x: direction+'_'+x for x in avg.columns.tolist()})
	return avg

def calcMedian(df, direction):
	incwt = df.loc[df[direction] != '0']
	output = incwt.groupby(['year', direction])['income'].median().reset_index()	
	output = output.pivot('year', direction, 'income')
	output = output.rename(columns={x: direction+'_'+x for x in output.columns.tolist()})
	return output


'''
# Get unweighted counts by demographic variables EXCEPT wealth/ income
df = pd.read_csv("M:/senior living/data/psid data/allvars_st.csv")
inc_yr_mask = ((df['income']>0) & (~df['year'].isin([1973, 1974, 1982])))
incwt = df.loc[inc_yr_mask, ['indweight', 'income', 'year',\
	 'Housing Category', 'Trans_to', 'Trans_from', 'moved', 'hstructure']]
incwt['weighted_income'] = incwt['income'] * incwt['indweight']
getDemog(df)
'''

# Get unweighted average and median stats for wealth and income
df = pd.read_csv("M:/senior living/data/psid data/allvars_demo.csv")
getIncomeStats(df)

#income('Trans_to', 'to', df)

#print (incwt['income']*incwt['indweight']).median()

#print df.loc[((df['income']>0) & (df['year']==2011) & (df['moved'] == 1) & (df['Trans_to'] =='SFO/ SFR')), 'income'].describe()
#print income('Trans_from', "From", df)