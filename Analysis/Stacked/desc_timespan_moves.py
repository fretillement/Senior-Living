import pandas as pd
'''
This program counts the number of moves and number of 
years a respondent is in the PSID. 
'''


df = pd.read_csv('M:/Senior Living/Data/PSID Data/timespan_moves.csv')

def timespan(df): 
	output = pd.DataFrame(df.groupby('unique_pid').size())
	output = output.rename(columns={0: 'num_years'})
	return output 

def numMoves(df):
	df.loc[df['moved2']==5, 'moved2'] = 0
	output = pd.DataFrame(df.groupby('unique_pid')['moved2'].sum())
	output = output.rename(columns={'moved2': 'num_moves'})
	return output

#timespan_df = timespan(df)
#nummoves_df = numMoves(df)
# Merge the dfs 
#output = timespan_df.merge(nummoves_df, right_index=True, left_index=True, how='outer')
# print output.head(30)
# Write to a csv
#output.to_csv('M:/Senior Living/Data/PSID Data/timespan_moves.csv')

def twoway(df=df): 
	df['num_years_bucket'] = pd.cut(df['num_years'], bins=range(0,31,5), right=False,\
					 retbins=False) 
	df['num_moves_bucket'] = pd.cut(df['num_moves'], bins=range(0,31,5), right=False,\
					 retbins=False) 
	output = pd.DataFrame(df.groupby(['num_moves_bucket', 'num_years_bucket']).size()).reset_index()
	output = output.pivot('num_moves_bucket', 'num_years_bucket', 0)
	return output 
print twoway()
twoway().to_csv('M:/test.csv')

def buckets(var, df=df): 
	df[var+'_bucket'] = pd.cut(df[var], bins=range(0,31,5), right=False,\
					 retbins=False) 
	output = pd.DataFrame(df.groupby(var+'_bucket').size())
	output = output.rename(columns={0: 'count'}).sort('count',ascending=False)
	return output 

def mean(var, df=df): 
	return df[var].mean()

def median(var, df=df):
	return df[var].median()

def pctile(var, pct, df=df):
	return df[var].quantile(pct)

#print pctile('num_moves', .9)
#print pctile('num_years', .9)
#df['num_moves'].hist()
#print mean('num_moves')
#print mean('num_years')
#print df['num_moves'].describe()
#print buckets('num_years').to_csv('M:/test.csv')