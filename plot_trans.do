


insheet using "M:/senior living/data/psid data/hcatnums_1968-1984.csv", clear

label var to_mfrmfo "To Multifamily"
label var to_sfosfr "To SF"
label var to_seniorhousing "To Senior Housing"
label var to_shared "To Shared"

label var from_mfrmfo "From MF"
label var from_sfosfr "From SF"
label var from_seniorh "From seniorh"
label var from_shared "From shared"



* Graphs TO
graph bar to_mfrmfo to_sfosfr to_seniorh to_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of Transitions Chosen") stack percent legend(label(1 MF) label(2 SF) label(3 "To senior housing") label(4 "To shared")) 
graph bar to_mfrmfo to_sfosfr to_seniorh to_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of Transitions Chosen") stack legend(label(1 MF) label(2 SF) label(3 "To senior housing") label(4 "To shared")) 

* Graphs FROM
graph bar to_mfrmfo to_sfosfr to_seniorh to_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of Transitions Chosen") stack percent legend(label(1 MF) label(2 SF) label(3 "To senior housing") label(4 "To shared"))
graph bar from_mfrmfo from_sfosfr from_seniorh from_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of Transitions From") stack legend(label(1 "From MF") label(2 "From SF") label(3 "From senior housing") label(4 "From shared"))

* Graph EXISTING
graph bar MF SF seniorhousing shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Existing share of housing categories") stack percent legend(label(1 MF) label(2 SF) label(3 "Senior housing") label(4 "Shared"))
graph bar MF SF seniorhousing shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Existing share of housing categories") stack legend(label(1 MF) label(2 SF) label(3 "Senior housing") label(4 "Shared"))


