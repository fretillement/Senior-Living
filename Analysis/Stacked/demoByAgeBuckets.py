from __future__ import division
import pandas as pd
from wealth_Income_vars import w_median
import numpy as np
import os 

'''


'''
# Change directory to data 
os.chdir("M:/Senior living/data/psid data/")

# This function takes in a dataframe and calculates
# weighted median net worth
def medNetWorth(df): 
	# Keep only years with wealth info 
	years = [1984, 1989, 1994, 1999, 2001, 2003, 2005, 2007, 2009, 2011]
	df = df.loc[df['year'].isin(years), :]

	# Calculate weighted median and return 
	median = w_median(df,'impwealth', 'famwt')
	return median

# This function takes in a df and calculates the weighted
# median highest grade completed 
def medEducation(agedf): 
	median = w_median(agedf, 'educ', 'indweight')
	return median 

# Takes a df, computes value counts and share of each categorical variable
def pctDemographic(agedf, var): 
	# If urban, keep only years for which there was info
	agebucket = agedf['age bucket'].iloc[0]
	if var == 'urban-rural category': agedf = agedf.loc[agedf['year'].isin(range(1985,2013,1)), :]
	categories = agedf[var].unique()
	output = {c:0 for c in categories}
	if agedf.empty: return pd.DataFrame({agebucket: output}).T
	for label in categories: 
		count = agedf.loc[agedf[var]==label, 'indweight'].sum()
		output[label] = count / agedf['indweight'].sum()
	return pd.DataFrame({agedf['age bucket'].iloc[0]: output}).T


def ageBuckets(df): 
	buckets = [[x, x+15] for x in range(1, 91, 15)]
	df['age bucket'] = pd.cut(df['age2'], bins=range(0, 107, 15))
	return df


if __name__ == "__main__": 
	test = {'impwealth': [1, 2, 3, 4, 5, 6], 'famwt': [1.1, 3, 1.7, .1, 1, 2]}

	# Read in the dataframe
	df = pd.read_csv('M:/senior living/data/psid data/complete_st.csv')

	# Select those who moved
	#df = df.loc[df['moved2']==1, :]

	# Select those who moved to shared
	#df = df.loc[df['Trans_to']=="Shared", :]

	# Select those who moved to SF 
	#df = df.loc[df['Trans_to'] == 'SFO/ SFR', :]

	# Select those who moved to MF 
	#df = df.loc[df['Trans_to'] == 'MFR/ MFO', :]

	# Select those who moved to Senior
	#df = df.loc[df['Trans_to'] == 'Senior housing', :]


	# Select those who are occupied in SFR
	#df = df.loc[df['Housing Category']=='SFO/ SFR', :]

	# Select those who are occupied in MF
	#df = df.loc[df['Housing Category']=='MFR/ MFO', :]

	# Select those  who are occupied in Senior
	#df = df.loc[df['Housing Category']=='Senior housing', :]


	# Select those who are occupied in shared
	#df= df.loc[df['Housing Category']=='Shared', :]

	transvars = ['Trans_to', 'Trans_from', 'Housing Category']
	for t in transvars: 
		df.loc[df[t] == 'Senior housing', t] = "Senior"
		df.loc[df[t] == 'SFO/ SFR', t] = "SF"
		df.loc[df[t] == 'MFR/ MFO', t] = "MF"
		df.loc[df[t] == 'Other/ Mobile Home', t] = "Other"
	
	df.to_csv('M:/senior living/data/psid data/complete_st.csv')


	'''
	# Generate 15-year age buckets
	df = ageBuckets(df)

	# Groupby age bucket
	dfgr_age = df.groupby('age bucket')

	# For each age bucket, get the following: percent urban, percent white, percent black, and percent other 
	test = dfgr_age.get_group('(15, 30]')
	
	race_fn = lambda x: pctDemographic(x, 'race')
	race_df = dfgr_age.apply(race_fn)
	race_df = race_df.loc[:, ['Black or African-American', 'White', 'Asian']].reset_index()
	race_df = race_df.drop(['level_1'], axis=1)
	race_df = race_df.set_index('age bucket')

	urban_fn = lambda x: pctDemographic(x, 'urban-rural category')
	urban_df = pd.DataFrame(dfgr_age.apply(urban_fn))
	urban_df = urban_df.rename(columns={'No info': 'No urbanicity info'}).reset_index()
	urban_df = urban_df.drop(['level_1'], axis=1)
	urban_df = urban_df.set_index('age bucket')
	print urban_df.index

	pcts = urban_df.join(race_df)#.reset_index().set_index('age bucket')
	print pcts

	#pcts = urban_df.join(race_df, how='left').set_index('age bucket')	
	if 'level_1' in list(pcts): pcts = pcts.drop('level_1', axis=1)
	

	# For each age bucket, get weighted median net worth and completed education
	wealth_df = pd.DataFrame(dfgr_age.apply(medNetWorth))
	wealth_df = wealth_df.rename(columns={0: 'Median net worth'})

	educ_df = pd.DataFrame(dfgr_age.apply(medEducation))
	educ_df = educ_df.rename(columns={0: 'Median completed education'})

	meds = wealth_df.join(educ_df, how='left')
	print meds

	# Merge medians with percents; write to csv
	output = pcts.join(meds, how='outer')
	output.to_csv('15yr_demos_toMF.csv')
	'''
	'''
	# Create urban-rural categories
	df['urban-rural category'] = "No urbanicity info"
	urban_mask = ((df['urban-rural code'].isin(range(1,6))))
	rural_mask = ((df['urban-rural code'].isin(range(6,9))))
	df.loc[urban_mask, 'urban-rural category'] = 'urban'
	df.loc[rural_mask, 'urban-rural category'] = 'rural'
	df.to_csv('M:/senior living/data/psid data/complete_st.csv', index=False)
	'''