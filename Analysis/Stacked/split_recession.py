import pandas as pd 
from count_demog import *

df = pd.read_csv('M:/Senior living/data/psid data/complete_st.csv')

def countByAgeUrbanTrans(transvar, timestub, df):
	# Relabel urban variable
	df.loc[df['urban-rural code'].isin(range(1,6)), 'urban-rural code'] = 'urban'
	df.loc[df['urban-rural code'].isin([9, 8, 7, 6]), 'urban-rural code'] = 'rural'
	df.loc[df['urban-rural code'].isin([99, 0]), 'urban-rural code'] = 'no info'

	# Restrict only those who have had a transition
	def urbanType(transvar, urbantype, df=df): 
		df = df.loc[df['urban-rural code']==urbantype, :]
		if transvar in ['Trans_to', 'Trans_from']: 
			#print len(df.loc[df[transvar] == '0'])
			df = df.loc[df[transvar] != '0', :]
		output = pd.DataFrame(df.groupby(['age2', transvar]).size())
		output = output.reset_index()
		output = output.rename(columns={0:'count', 'age2':'age'})
		output = output.pivot('age', transvar, 'count')
		output['urban-rural code'] = urbantype
		return output 

	urbantypes = ['no info', 'rural', 'urban']
	temp = pd.DataFrame()
	for u in urbantypes:
		output = urbanType(transvar, u)
		temp = temp.append(output) 
	return temp



def countByAgeTrans(transvar, df):
	# Restrict only those who have had a transition
	if transvar in ['Trans_to', 'Trans_from']: 
		#print len(df.loc[df[transvar] == '0'])
		df = df.loc[df[transvar] != '0', :]
	output = pd.DataFrame(df.groupby(['age2', transvar]).size())
	output = output.reset_index()
	output = output.rename(columns={0:'count', 'age2':'age'})
	output = output.pivot('age', transvar, 'count')
	return output 



def getIncomeStats(df, var, timespan, output_fpath): 
	# Select only nonzero income values and years in timespan for which there is 
	# info on the person's housing structure
	inc_yr_mask = ((df[var]>0) & (~df['year'].isin([1973, 1974, 1982])))	 	
	t_mask = ((df['year'].isin(timespan)))
	df = df.loc[inc_yr_mask & t_mask, [var, 'indweight', 'year', 'unique_pid',\
	 'Housing Category', 'Trans_to', 'Trans_from', 'moved', 'hstructure']]
	
	# Generate a weighted income variable 
	df['weighted_var'] = df[var] * df['indweight']
	
	# Generate a time string for output file
	timestub = str(int(min(timespan))) + '_' + str(int(max(timespan)))

	# Calculate and write median to csv for each direction of transtion (to, from, current)
	med_output = calcMedian(df, var, 'Trans_to')
	med_output = med_output.merge(calcMedian(df, var, 'Trans_from'), right_index=True, left_index=True)
	med_output = med_output.merge(calcMedian(df, var, 'Housing Category'), right_index=True, left_index=True)
	#med_output.to_csv(output_fpath+'med_' + var + '_' + timestub + '.csv', index=False)
	print 'writing'
	med_output.to_csv('med'+var+timestub+'.csv')

	# Calculate and write weighted avg to csv 
	avg_output = calcWavg(df, 'Trans_to')
	avg_output = avg_output.merge(calcWavg(df, 'Trans_from'), right_index=True, left_index=True)
	avg_output = avg_output.merge(calcWavg(df, 'Housing Category'), right_index=True, left_index=True)
	#avg_output.to_csv(output_fpath+'avg_' + var + '_' + timestub +'.csv', index=False)
	print 'writing'
	avg_output.to_csv('avg'+var+timestub+'.csv')

if "__name__" == "__main__":
	timespans = [range(2007,2013,2), range(1999,2007,2)]
	output_fpath = 'M:/senior living/data/psid data/later third/'
	for t in timespans: 
		temp_df = df.loc[df['year'].isin(t), :]
		#getIncomeStats(df, 'impwealth', t, output_fpath)
		transtypes = ['Trans_to', 'Trans_from', 'Housing Category']
		for transvar in transtypes: 
			output = countByAgeTrans(transvar, temp_df)	
			datestub = str(int(min(t)))+'-'+str(int(max(t)))
			#output = countByAgeUrbanTrans(transvar, datestub, temp_df)
			output.to_csv('M:/senior living/data/psid data/later third/'+ transvar + datestub+'.csv')
			#print output.head(10)
		



#output = mergeBeale()
#output.to_csv('M:/test.csv')
#print countByAgeTrans('Trans_to').head(20)
#output = pd.read_csv('M:/test.csv')
#output = output.groupy('unique_pid')
#def fillAges(group):

















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