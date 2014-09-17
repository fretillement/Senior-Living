
*"1985-1995" "1968-1984" 

foreach date in "1996-2011" "1985-1995" {
	foreach geo in "urban" "rural" { 
		* Read data
		insheet using "M:/senior living/data/psid data/hcatnums_`geo'_`date'.csv", clear
		
		*Clean up vars 
		drop from_0 to_0 
		*drop v2 v3 if "`date'" == "1996-2011"
		
		rename to_mfrmfo to_MF
		rename to_sfosfr to_SF
		rename to_seniorhousing to_seniorh
		
		rename from_mfrmfo from_MF
		rename from_sfosfr from_SF
		
		rename mfrmfo current_MF
		rename sfosfr current_SF
		rename seniorhousing current_seniorh
		rename shared current_shared
		
		label var to_MF "To Multifamily"
		label var to_SF "To SF"
		label var to_seniorh "To Senior Housing"
		label var to_shared "To Shared"
		
		label var from_MF "From MF"
		label var from_SF "From SF"
		label var from_seniorh "From seniorh"
		label var from_shared "From shared"
		
		*Optional: uncomment to outsheet 
		outsheet using "M:/senior living/data/psid data/housingcats_`geo'_`date'.csv", comma replace


		/*Create and save graphs
		* Graphs TO
		graph bar to_MF to_SF to_seniorh to_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of `geo' transitions chosen, `date'") stack percent legend(label(1 "To MF") label(2 "To SF") label(3 "To senior housing") label(4 "To shared")) 
		gr export "M:/senior living/graphs/Transitions/SharesTo_`geo'_`date'.pdf", as(pdf) replace		

		graph bar to_MF to_SF to_seniorh to_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Count of `geo' transitions chosen, `date'") stack legend(label(1 "To MF") label(2 "To SF") label(3 "To senior housing") label(4 "To shared")) 
		gr export "M:/senior living/graphs/Transitions/CountsTo_`geo'_`date'.pdf", as(pdf) replace

		* Graphs FROM
		graph bar from_MF from_SF from_seniorh from_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Share of `geo' transitions from, `date'") stack percent legend(label(1 "From MF") label(2 "From SF") label(3 "From senior housing") label(4 "From shared"))
		gr export "M:/senior living/graphs/Transitions/SharesFrom_`geo'_`date'.pdf", as(pdf) replace
		
		graph bar from_MF from_SF from_seniorh from_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Counts of `geo' transitions from, `date'") stack legend(label(1 "From MF") label(2 "From SF") label(3 "From senior housing") label(4 "From shared"))
		gr export "M:/senior living/graphs/Transitions/CountsFrom_`geo'_`date'.pdf", as(pdf) replace

		* Graph EXISTING
		graph bar current_MF current_SF current_seniorh current_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Existing `geo' share of housing categories, `date'") stack percent legend(label(1 MF) label(2 SF) label(3 "Senior housing") label(4 "Shared"))
		gr export "M:/senior living/graphs/Transitions/SharesExisting_`geo'_`date'.pdf", as(pdf) replace
		
		graph bar current_MF current_SF current_seniorh current_shared if age2 > 25, over(age2, label(alternate labsize(vsmall))) title("Existing `geo' counts of housing categories, `date'") stack legend(label(1 MF) label(2 SF) label(3 "Senior housing") label(4 "Shared"))
		gr export "M:/senior living/graphs/Transitions/CountsExisting_`geo'_`date'.pdf", as(pdf) replace*/
	}
}
