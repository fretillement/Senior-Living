
/*This program simply reads the full PSID data, and saves in dta and csv format*/ 

clear 

*Run dictionary file to get labels 
run "/Users/ShruthiVenkatesh/Documents/Senior-Living/PSID_clean/J175970.do"
*run "M:/Senior Living/Data/PSID Data/All_weights/J174506.do" 

*Save in stata format 
*save "/Users/ShruthiVenkatesh/Documents/Senior Living Project/PSID Data/
*save "M:/Senior Living/Data/PSID Data/All_weights/J174506.dta", replace 

*Export to csv 
*outsheet using "M:/Senior Living/Data/PSID Data/All_weights/J174506.csv", comma noquote replace 
outsheet using "/Users/ShruthiVenkatesh/Documents/Senior Living Project/PSID Data/J175970.csv", comma noquote replace


*Save a variable description
*descsave, saving("M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.dta", replace)
descsave, saving("/Users/ShruthiVenkatesh/Documents/Senior Living Project/J175970.dta", replace) 
use "/Users/ShruthiVenkatesh/Documents/Senior Living Project/J175970.dta", clear
*use "M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.dta", clear
*outsheet using "M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.csv", comma replace
outsheet using "/Users/ShruthiVenkatesh/Documents/Senior-living/J175970_desc.csv", comma replace

