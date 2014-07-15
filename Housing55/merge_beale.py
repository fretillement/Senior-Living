
import pandas as pd 

# Beale data into df 
y = 1991 
bealedata = 'M:/Senior Living/Data/PSID Data/Beale Urbanicity/newbeale8511.csv'
#bealedata = '/Users/ShruthiVenkatesh/Documents/newbeale8511/newbeale8511.csv'
beale = pd.read_csv(bealedata)

# Yearly data
fpath = 'M:/Senior Living/Data/PSID Data/years/' + str(y) + '.csv'
#fpath = '/users/ShruthiVenkatesh/Documents/Senior Living Project/Data/' + str(y) + '.csv'
vfpath = 'M:/Senior Living/Data/PSID Data/agecohort_vars.csv'
famintnum = (pd.read_csv(vfpath).groupby('year').get_group(y)).loc[0, 'famintnum']
ydf = pd.read_csv(fpath)

# Isolate yearly obs from Beale df
yBeale = pd.DataFrame(beale.loc[beale['CBV2'] == y])

# Merge yearly obs to yearly data by fam id



# Outsheet 