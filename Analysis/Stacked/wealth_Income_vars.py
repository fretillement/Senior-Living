from __future__ import division
import pandas as pd
'''
This is a set of functions that examines wealth and income
variables of the most recent complete PSID stacked file. 

The stacked dataframe is constructed with getComplete.py 
'''

def w_median(df, var='impwealth', weight='famwt'):
	if df.empty: return 
	# Sort impwealth in ascending order 
	df = df.sort(var)

	# Get a cumulative sum of weight
	df['w_cumsum'] = df[weight].cumsum(axis=1)

	# Find the 50th percentile of observations
	p50 = df[weight].sum()*(.5)

	# Get the corresponding index 
	p50_index = df.loc[df['w_cumsum'] <= p50, var].last_valid_index()
	if (len(df.index) == 1): p50_index = df[var].last_valid_index() # If there's only one obs return the same index

	# The median is then the wealth measure that pertains to the 50th percentile index
	median = df.ix[p50_index, var]
	return median


def yearlyMedianWealth(complete_df): 
	# Keep only years that have wealth observations
	year_mask = ((complete_df['year'].isin([1984, 1989, 1994, 1999, 2001,\
								  2003, 2005, 2007, 2009, 2011])))
	complete_df = complete_df.loc[year_mask, :]

	# Keep only families that are participating in the survey for each year

	# Groupby year 
	yr_complete_df = complete_df.groupby('year')

	# For each yearly group, compute median income
	#med = lambda x: w_median(x)
	output = pd.DataFrame(yr_complete_df['impwealth'].median())
	return output 


df = pd.read_csv('M:\Senior Living\Data\PSID Data\complete_st.csv')
year_df = yearlyMedianWealth(df)


def yearlyWealthPercentile(age_df, year_df=year_df):
	# Keep only years for which there IS wealth data 
	year_mask = ((age_df['year'].isin([1984, 1989, 1994, 1999, 2001,\
								  2003, 2005, 2007, 2009, 2011])))
	age_df = age_df.loc[year_mask,:]
	if age_df.empty: return pd.Series()

	# Calculate median SHARE of overall median for each housing category in each year
	medianshare = lambda x: pd.DataFrame(x['impwealth'].median() / year_df.ix[x['year'], 'impwealth']).iloc[0]
	medians = age_df.groupby(['year', 'Housing Category']).apply(medianshare)
	medians = medians.reset_index()
	#
	medians = medians.pivot('year', 'Housing Category', 'impwealth')
	#return medians

	# Calculate average percentile over the years 
	avg_pctile = medians.mean(axis=0)
	return avg_pctile

def avgPercentileByAge(complete_df, year_df=year_df): 
	output = complete_df.groupby('age2').apply(yearlyWealthPercentile)
	output = output.reset_index()
	output = output.rename(columns={'age2': 'age', 0L: 'Share of median wealth'})
	output = output.pivot('age', 'Housing Category', 'Share of median wealth')
	return output

output = avgPercentileByAge(df)
output.to_csv('M:/senior living/data/psid data/Demographics/pctile_wealth.csv')


'''
# Calculate median wealth by 5-year age bucket and 
# housing occupancy (vars age2 and Housing Category) for years
# in which wealth was measured.
def medWealth(complete_df): 
	# Keep only years for which wealth is measured and 
	# obs is <= 100 years old. 
	year_mask = ((complete_df['year'].isin([1984, 1989, 1994, 1999, 2001,\
								  2003, 2005, 2007, 2009, 2011])))
	age_mask = ((complete_df['age2'] <= 100))	
	complete_df = complete_df.loc[year_mask & age_mask, :]

	# Set all observations with NEGATIVE wealth as 0 
	#complete_df.loc[(complete_df['impwealth'] < 0), 'impwealth'] = 0
	complete_df = complete_df.loc[complete_df['impwealth'] > 0, :]

	# Generate 5-year age2 bins
	complete_df['Age Bucket'] = pd.cut(complete_df['age2'], bins=range(0,100,5), retbins=False)
	
	# Groupby housing category and agebucket 
	gr_complete_df = complete_df.groupby(['Age Bucket', 'Housing Category'])

	# Calculate median 
	med_fn = lambda x: w_median(x)
	output = pd.DataFrame(gr_complete_df.apply(med_fn))
	
	# Pivot; sort by ascending age bucket
	output.reset_index(inplace=True)
	output = output.rename(columns={0: 'impwealth'})
	print output.columns.tolist()
	output = output.pivot('Age Bucket', 'Housing Category', 'impwealth')
	output.reset_index(inplace=True)
	output.sort('Age Bucket', inplace=True)
	return output
'''
 


#df.to_csv('M:\Senior Living\Data\PSID Data\med_wealth_age.csv', index=False)