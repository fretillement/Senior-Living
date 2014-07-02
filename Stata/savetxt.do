
/*This program simply reads the full PSID data, and saves in dta and csv format*/ 

clear 

*Run dictionary file to get labels 
run "M:/Senior Living/Data/PSID Data/All_weights/J174506.do" 

*Save in stata format 
save "M:/Senior Living/Data/PSID Data/All_weights/J174506.dta", replace 

*Export to csv 
outsheet using "M:/Senior Living/Data/PSID Data/All_weights/J174506.csv", comma noquote replace 

*Save a variable description
descsave, saving("M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.dta", replace)
use "M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.dta", clear
outsheet using "M:/Senior Living/Data/PSID Data/All_weights/J174506_desc.csv", comma replace


