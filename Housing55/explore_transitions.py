from __future__ import division
import matplotlib.pyplot as plt
import pandas as pd

''' 
This program conducts exploratory analysis of elderly 
transitions esp. to senior living facilities in the most 
recent raw PSID file (current file = J177301.txt)
'''
# Edit filepaths 
f_panel =  "M:/Senior Living/Data/PSID Data/Panel/55plus_trans75-84.csv"
panelvars = ['unique_pid', 'numtrans'] +\
			['age_trans' + x for x in map(str,range(1,25))] +\
		    ['trans' + x for x in map(str, range(1,25))] 


# Read in datasets
fullpanel = pd.read_csv(f_panel)

test = fullpanel.loc[fullpanel['numtrans'] > 0, ['numtrans', 'age_trans1', 'age_trans2']]
test['age_trans1'].hist()
plt.show()