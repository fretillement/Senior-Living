from __future__ import division
import pandas as pd 


'''
This script returns counts by housing categories of economic &
demographic characteristics of PSID panel members (file: J178148_edits.csv)
'''
# Set output filepath for demographic variable counts 
output_fpath = "M:/senior living/data/psid data/demographics/"

# Rename variables accordingly 
def renameEduc(df): 
	print "Renaming educ"
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
	print "Renaming race"
	dict_1968 = {0: 'N/A', 1: 'White', 2: 'Black or African-American', 3: 'Puerto Rican, Mexican', 7:'Other', 4: 'Other', 5: 'N/A', 9: 'N/A'}
	dict_1984 = {0: 'N/A', 1: 'White', 2: 'Black or African-American', 3: 'Puerto Rican, Mexican', 4:'Asian', 7: 'Other', 9: 'N/A'}
	dict_2011 = {0: 'N/A', 1: 'White', 2: 'Black or African-American', 3: 'American Indian', 4: 'Asian',\
		 5: 'Native Hawaiian', 6: 'Mentions color other than black or white', 7: 'Other', 8: "N/A, Don't know",\
		  9: "N/A, Don't know"}
	mask_1968 = ((df['year'] == 1968))
	mask_1984 = ((df['year'].isin(range(1969,1986))))
	mask_2011 = ((df['year'].isin(range(1986,1998)+range(1999,2013,2))))
	for code in dict_1968: 
		df.loc[mask_1968 & (df['race']==code), 'race'] = dict_1968[code]
	for code in dict_1984: 	
		df.loc[mask_1984 & (df['race']==code), 'race'] = dict_1984[code]
	for code in dict_2011: 
		df.loc[mask_2011 & (df['race']==code), 'race'] = dict_2011[code]
	return df 

def renameMarital(df): 
	print "Renaming marital"
	df.loc[(df['mar'] > 0), 'mar'] = "Married"
	df.loc[(df['mar'] == 0), 'mar'] = "Single"
	return df 

def renameGender(df): 
	print "Renaming gender"
	df_gr = df.groupby('unique_pid')
	def recodeGender(group):
		#print group['unique_pid'].iloc[0] 
		if len(~group.loc[(group['gender'] >0), 'gender'].index)>0: gender = group.loc[(group['gender'] >0), 'gender'].iloc[0]
		else: gender = 0
		if gender == 1: group.loc[:, 'gender'] = 'Male' 
		if gender == 2: group.loc[:, 'gender'] = 'Female'
		return group
	output = df_gr.apply(recodeGender)
	return output


def getDemog(df, demvars=['gender', 'mar', 'race', 'educ'], output_fpath=output_fpath):
	#df = renameGender(renameMarital(renameRace(renameEduc(df))))
	#df = df.drop(['Unnamed: 1', 'index', 'unique_pid.1'], axis=1)
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
		output.to_csv(output_fpath +  d + "_count.csv", index=True)


# Call functions to calc mean and median income and wealth
# Write to a csv
#timespan = [1973, 1974, 1982]
def getIncomeStats(df, var, timespan, output_fpath): 
	inc_yr_mask = ((df[var]>0) & (~df['year'].isin([1973, 1974, 1982])))
	# Select only nonzero income values and years for which there is info on 
	# the person's housing structure 
	t_mask = ((df['year'].isin(timespan)))

	df = df.loc[inc_yr_mask & t_mask, [var, 'indweight', 'year', 'unique_pid',\
	 'Housing Category', 'Trans_to', 'Trans_from', 'moved', 'hstructure']]
	
	# Generate a weighted income variable 
	df['weighted_var'] = df[var] * df['indweight']
	

	timestub = str(int(min(timespan))) + '_' + str(int(max(timespan)))

	# Calculate and write median to csv for each direction of transtion (to, from, current)
	med_output = calcMedian(df, var, 'Trans_to')
	med_output = med_output.merge(calcMedian(df, var, 'Trans_from'), right_index=True, left_index=True)
	med_output = med_output.merge(calcMedian(df, var, 'Housing Category'), right_index=True, left_index=True)
	#med_output.to_csv(output_fpath+'med_' + var + '_' + timestub + '.csv', index=False)
	print 'writing'
	med_output.to_csv('med'+var+timestub+'.csv', index=False)

	# Calculate and write weighted avg to csv 
	avg_output = calcWavg(df, 'Trans_to')
	avg_output = avg_output.merge(calcWavg(df, 'Trans_from'), right_index=True, left_index=True)
	avg_output = avg_output.merge(calcWavg(df, 'Housing Category'), right_index=True, left_index=True)
	#avg_output.to_csv(output_fpath+'avg_' + var + '_' + timestub +'.csv', index=False)
	print 'writing'
	avg_output.to_csv('avg'+var+timestub+'.csv', index=False)


# Calculate weighted average for a given direction (to, from, or current)	
def calcWavg(df, direction): 
	wavg = lambda x: x['weighted_var'].sum() / x['indweight'].sum()
	incwt = df.loc[df[direction] != '0']
	avg = incwt.groupby(['year', direction]).apply(wavg)
	avg = avg.reset_index().pivot('year', direction, 0)
	avg = avg.rename(columns={x: direction+'_'+x for x in avg.columns.tolist()})
	return avg

# Calculuate median for a given direction (to, from, current)
def calcMedian(df, var, direction):
	incwt = df.loc[df[direction] != '0']
	output = incwt.groupby(['year', direction])[var].median().reset_index()	
	output = output.pivot('year', direction, var)
	output = output.rename(columns={x: direction+'_'+x for x in output.columns.tolist()})
	return output

# Count number of people in each demographic category by age and housing OCCUPANCY
def countHousingByDemo(df, dem):
	hcats = ['Housing Category']
	temp_grdf = pd.DataFrame()
	for c in hcats: 
		tempdf = df.loc[df[c] != '0', :]
		grdf = pd.DataFrame(tempdf.groupby([dem, 'age'])[c].value_counts().reset_index())
		grdf = grdf.rename(columns={'level_2':c, 0:'count'})
		for d in df[dem].value_counts().index.tolist(): 
			output = grdf.loc[grdf[dem]==d, :]
			output = output.pivot('age', c, 'count')
			output[dem] = d
			#newcols = {n: c+'_'+n for n in output.columns.tolist()}
 			temp_grdf = temp_grdf.append(output)






'''
# Get unweighted counts by demographic variables EXCEPT wealth/ income
# Read in full stacked df
#df = pd.read_csv("M:/senior living/data/psid data/complete_st.csv")
df = pd.read_csv('M:/test.csv')

# Rename race, education, gender, and marital variables 
df = renameRace(df)
df = renameEduc(df)
df = renameGender(df)
df = renameMarital(df)
df.to_csv("M:/senior living/data/psid data/complete_st.csv")


# Get counts by race, education, gender, and marital status 
# for each age.
df = pd.read_csv("M:/test.csv")
demo = ['race','educ', 'gender', 'mar']
for dem in demo: 
	countHousingByDemo(df, dem)


# Calculate counts by race, education, gender, and marital status 
#getDemog(df)

# Get median and mean income by year
#getIncomeStats(df, 'income')

# Get median and mean wealth by year 
#getIncomeStats(df, 'impwealth')
'''