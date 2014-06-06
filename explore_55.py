import numpy as np 
import pandas as pd
from pandas import Series, DataFrame, Index
import csv


#Read in variable description sheet
#desc = csv.DictReader(open("M:/Senior Living/Data/PSID Data/complete_PSID_desc.csv", 'r'))
desc = pd.read_csv("M:/Senior Living/Data/PSID Data/complete_PSID_desc.csv")

#Isolate variables for each year
years = range(1968, 2012)
yvars = {}
for y in years: 
	temp = (desc[desc['year'] == y])['varlab'].tolist() 
	yvars[y] = [' '.join(t.split()) for t in temp] 
#	print test 



print yvars 

def isolateVars(vardesc, df): 

	return

#Place variables in dict 

#Rewrite variable names to make more sense 

#Replace variable names in each dict

#Merge dict to create a single database of vars
#Must be consistent across years

#Read in main spreadsheet into seperate dfs by year 
#Include only people older than 55 
#Must have consistent variable names 

