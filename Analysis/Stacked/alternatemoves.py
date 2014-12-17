import pandas as pd 


# Read csv
df = pd.read_csv("M:/test.csv")

# Groupby unique_pid
gr = df.groupby('unique_pid')
test = gr.get_group('1000_1')

# 
def moved3(group): 
	group = group.reset_index()
	group['moved3'] = 0
	lines = group.iterrows()
	for item in lines: 
		(index, line) = item
		if index > 0: 
			if (line['Housing Category'] != group.ix[(index-1), 'Housing Category']) | (line['moved2'] == 1): 
				group.loc[index, 'moved3'] = 1
		else: 
			group.loc[index, 'moved3'] = 0
	return group

# Construct 'Trans_to' variable
def markHousingTo(df):
	#df = self.markShared() 
	df['Trans_to_alt'] = 0
	moved_mask = (df['moved3']==1)
	df.loc[moved_mask, 'Trans_to_alt'] = df['Housing Category']
	return df

# Construct 'Trans_from' AND 'Trans_to' variable
def markHousingFrom(df):
	df = markHousingTo(df) 
	# Fill in empty hstructure values 
	mobile_home_other = ((df['Housing Category'].isin(['Mobile Home/ trailer', 0])))
	df.loc[mobile_home_other, 'Housing Category'] = 'Other/ Mobile Home'
	grouped = df.groupby('unique_pid')
	def getFrom(gr): 
		gr['Trans_from_alt'] = 0
		if gr.loc[(gr['moved3']==1), 'moved3'].sum() > 0: 
			gr_iter = gr.iterrows()
			for l in gr_iter: 
				(index, line) = l
				print index
				if line['moved3'] == 1 and index-1 in gr.index: gr.loc[index, 'Trans_from_alt'] = gr.loc[index-1, 'Housing Category']		
		return gr 
	df = grouped.apply(getFrom)
	return df



#test = moved3(test)
#print test['moved3'].head()
output = gr.apply(moved3)
output.to_csv("M:/test_alt.csv", index=False)

output = pd.read_csv("M:/test_alt.csv")
output = markHousingFrom(output)
output.to_csv("M:/test_alt.csv", index=False)