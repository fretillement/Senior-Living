import numpy as np 
import pandas as pd
from pandas import Series, DataFrame, Index
import csv


#Read in variable description sheet
desc = pd.read_csv("M:/Senior Living/Data/PSID Data/complete_PSID_desc.csv")

#Take year, description file, isolate variables in dict 
years = range(1968, 2012)
def isolateVars(years, desc): 
	yvars = {}
	for y in years: 
		isoname = desc[desc['year'] == y]['name'].tolist()
		isolab = desc[desc['year'] == y]['varlab'].tolist() 
		yvars[y] = dict(zip([' '.join(t.split()) for t in isolab], isoname))  
	return yvars
vardict = isolateVars(years, desc)

#Read in main spreadsheet into seperate dfs by year 
fname = "M:/Senior Living/Data/PSID Data/complete_PSID_data.csv"
data = pd.read_csv(fname)
for y in years: 
	varlist = vardict[y].values()
	print varlist


#Include only people older than 55 
#Must have consistent variable names 

