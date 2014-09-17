
/*This program simply reads the full PSID data, and saves in dta and csv format*/ 
**Also saves a description of variables 

clear 

*Run dictionary file to get labels 
do "M:\senior living\data\psid data\J178127.do" 
*run "/users/shruthivenkatesh/Desktop/J177301/J177301.do"

*Save in stata format 
save "M:/Senior Living/Data/PSID Data/J178127.dta", replace 
*save "/users/ShruthiVenkatesh/Desktop/J177301.dta", replace

*Export to csv 
outsheet using "M:/Senior Living/Data/PSID Data/J178127.csv", comma noquote replace 
*outsheet using "/users/ShruthiVenkatesh/Desktop/J177301.csv", comma replace

*Save a variable description
descsave, saving("M:/Senior Living/Data/PSID Data/J178127_desc.dta", replace)
use "M:/Senior Living/Data/PSID Data/J178127_desc.dta", clear
rename vallab year
outsheet using "M:/Senior Living/Data/PSID Data/J178127_desc.csv", comma replace

*descsave, saving("/users/ShruthiVenkatesh/Desktop/J177301_desc.dta", replace)
*use "/users/ShruthiVenkatesh/Desktop/J177301_desc.dta", clear
*rename vallab year
*outsheet using "/users/ShruthiVenkatesh/Desktop/J177301_desc.csv", comma replace

