from fillMissing import *
from getStackedFrame import * 
import pandas as pd 

class identifyHousing: 
	'''
	Functions that attach transition variables to a stacked, 
	filled-in dataframe 
	'''
	def __init__(self, complete_df):
		self.df = complete_df

	# Place types of housing structures in a dict
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

	# Identify members of the panel who have been institutionalized
	# Based on method outlined in Ellwood and Kane (1990)	
	def labelInstAndHstruct(self, hstruct_dict=hstruct_dict):
		df = self.df 
		df['inst'] = 0
		ek1990_inst_mask = ((df['moved2'] == 1) & (df['whymoved'] == 7) \
				&  (df['numrooms'] <= 2) & (df['hstructure'] == 7))
		seniorh_mask = (df['seniorh'] == 1)
		instvar_mask = ((df['tinst'] == 3) | (df['tinst'] == 7))
		df.loc[ek1990_inst_mask | seniorh_mask | instvar_mask, 'inst'] = 1 
		# Rename hstructure vals to structure type they represent
		for n in hstruct_dict:
			hstruct_mask = ((df['hstructure'] == n))
			df.loc[hstruct_mask, 'hstructure'] = hstruct_dict[n]
		return df

	# First step in 'Housing Category' construction: Mark single family residences
	## NOTE: this function calls anyInst() AND renameHstructure() !!
	def markSF(self): 
		df = self.labelInstAndHstruct()
		df['Housing Category'] = 0
		sf_mask = ((df['hstructure'] == 'Single-family house'))
		owner_mask = ((df['htenure'] == 1))
		renter_mask = ((df['htenure'] == 5))
		#notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
		#sfo_mask =  ((sf_mask & owner_mask & notshared_mask) | (sf_mask & renter_mask & notshared_mask))
		df.loc[sf_mask, 'Housing Category'] = 'SFO/ SFR'
		return df

	# Second step: mark multi family residences
	def markMF(self):
	 	df = self.markSF()
	 	#notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
	 	mf_mask = ((df['hstructure'].isin(['Duplex/ 2-family house', 'Condo', 'Multifamily',\
	 				'Townhouse', 'Other'])))
	 	#renter_mask = ((df['htenure'].isin([5])))
	 	#owner_mask = ((df['htenure'].isin([1])))
	 	#mfr_mask = ((mf_mask & notshared_mask))
	 	df.loc[mf_mask, 'Housing Category'] = 'MFR/ MFO'
	 	return df

	# Third step: mark senior housing residences
	def markSeniorHousing(self): 
	 	df = self.markMF()
	 	#notshared_mask = ((~df['Housing Category'].isin(['Shared'])))
	 	#seniorh_mask = (((df['seniorh'].isin([1]) | (df['inst'].isin([1]))) & notshared_mask)) 
	 	seniorh_mask = (((df['seniorh'].isin([1]) | (df['inst'].isin([1])))))
	 	df.loc[seniorh_mask, 'Housing Category'] = 'Senior housing'
	 	return df

	# Fourth step: mark shared residences. 
	'''WARNING: this function overwrites existing values in 'Housing Category'!!'''
	def markShared(self): 
		df = self.markSeniorHousing() 
		#df['Housing Category'] = 0
		pre83_mask = ((df['year'] < 1983))
		post83_mask = ((df['year'] >= 1983))
		shared_mask = ((pre83_mask & (~df['relhead'].isin([0,1,2,8]))) | (post83_mask & (~df['relhead'].isin([0,10,20,90]))))
		df.loc[shared_mask, 'Housing Category'] = 'Shared'
		return df 

	# Construct 'Trans_to' variable
	def markHousingTo(self):
		df = self.markShared() 
		df['Trans_to'] = 0
		moved_mask = (df['moved2']==1)
		df.loc[moved_mask, 'Trans_to'] = df['Housing Category']
		return df

	# Construct 'Trans_from' AND 'Trans_to' variable
	def markHousingFrom(self):
		df = self.markHousingTo() 
		# Fill in empty hstructure values 
		mobile_home_other = ((df['Housing Category'].isin(['Mobile Home/ trailer', 0])))
		df.loc[mobile_home_other, 'Housing Category'] = 'Other/ Mobile Home'
		grouped = df.groupby('unique_pid')
		def getFrom(gr): 
			gr['Trans_from'] = 0
			if gr.loc[(gr['moved2']==1), 'moved2'].sum() > 0: 
				gr_iter = gr.iterrows()
				for l in gr_iter: 
					(index, line) = l
					print index
					if line['moved2'] == 1 and index-1 in gr.index: gr.loc[index, 'Trans_from'] = gr.loc[index-1, 'Housing Category']		
			return gr 
		df = grouped.apply(getFrom)
		return df
	'''
	# Construct the Beale Urbanicity (urban vs rural) variable
	def mergeBeale(self, beale_fpath=beale_fpath):
		self = self.markHousingFrom()
		df['urbancode'] = 0
		bealedf = pd.read_csv(beale_fpath).groupby(['CBV2', 'CBV3'])
		for group in bealedf: 
			(key, g) = group
			(year, famid) = key
			id_mask = ((df['year']==year) & (df['famid']==famid))
			df.loc[id_mask, 'urbancode'] = g['CBV4'].iloc[0]
			print key
		return df 
	'''
	def implement(self): 
		output = self.markHousingFrom()
		return output