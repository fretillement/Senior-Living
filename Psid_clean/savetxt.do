
/*This program simply reads the full PSID data, and saves in dta and csv format*/ 
**Also saves a description of variables 

clear 

*Run dictionary file to get labels 
run "M:/Senior Living/Data/PSID Data/J176012.do" 

*Save in stata format 
save "M:/Senior Living/Data/PSID Data/J176012.dta", replace 

*Export to csv 
outsheet using "M:/Senior Living/Data/PSID Data/J176012.csv", comma noquote replace 

*Save a variable description
descsave, saving("M:/Senior Living/Data/PSID Data/J176012_desc.dta", replace)
use "M:/Senior Living/Data/PSID Data/J176012_desc.dta", clear
rename vallab year 
outsheet using "M:/Senior Living/Data/PSID Data/J176012_desc.csv", comma replace


