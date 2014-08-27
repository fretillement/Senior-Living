from __future__ import division
import gc
import pandas as pd

''' 
This program conducts exploratory analysis of elderly 
transitions esp. to senior living facilities in the most 
recent raw PSID file (current file = J177301.txt)
'''
# Edit filepaths 
f_panel = 'M:/Senior living/Data/PSID Data/Panel/elderly_trans2.csv'
f_out = 'M:/test.csv'
panelvars = ['unique_pid', 'numtrans'] +\
			['age_trans' + x for x in map(str,range(1,25))] +\
		    ['trans' + x for x in map(str, range(1,25))] 
print panelvars

# Read in datasets
fullpanel = pd.read_csv(f_panel)
transpanel = fullpanel.loc[:, panelvars]
transpanel.to_csv(f_out, index=False)

gc.collect()