
/*This program simply reads the full PSID data, and saves in dta and csv format*/ 
**Also saves a description of variables 

clear 

*Point to most recent raw dataset
local recent J178730
*local recent J178704
*local recent J178305

*Run dictionary file to get labels 
do "M:/senior living/data/psid data/`recent'/`recent'.do" 
*run "/users/shruthivenkatesh/Desktop/J177301/J177301.do"

*Save in stata format 
save "M:/Senior Living/Data/PSID Data/`recent'.dta", replace 
*save "/users/ShruthiVenkatesh/Desktop/J177301.dta", replace

*Export to csv 
outsheet using "M:/Senior Living/Data/PSID Data/`recent'.csv", comma noquote replace 
*outsheet using "/users/ShruthiVenkatesh/Desktop/J177301.csv", comma replace

*Save a variable description
descsave, saving("M:/Senior Living/Data/PSID Data/`recent'_desc.dta", replace)
use "M:/Senior Living/Data/PSID Data/`recent'_desc.dta", clear
rename vallab year
outsheet using "M:/Senior Living/Data/PSID Data/`recent'_desc.csv", comma replace

*descsave, saving("/users/ShruthiVenkatesh/Desktop/J177301_desc.dta", replace)
*use "/users/ShruthiVenkatesh/Desktop/J177301_desc.dta", clear
*rename vallab year
*outsheet using "/users/ShruthiVenkatesh/Desktop/J177301_desc.csv", comma replace

/*Optional: Stata commands to fill in missing urban.rural.code values
insheet using "M:/senior living/data/Psid data/complete_st.csv"
by unique_pid, sort: gen urbancode85 = urbanruralcode if (moved != 1) & (year == 1985)
by unique_pid, sort: gen famcount = _n
by unique_pid, sort: replace urbanruralcode = urbancode85[famcount+1] if (year == 1984) & (urbancode > 0)
outsheet using "M:/senior living/data/Psid data/complete_st.csv", comma replace
*/
