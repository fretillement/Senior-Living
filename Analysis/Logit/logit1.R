library(dummies)
"
This script runs a logit model on the cleaned, most recent stacked
version of complete_st.csv. 

Complete_st.csv is built by getComplete.py

See that file for more info
"

# Set working directory
setwd("M:/senior living/code/senior-living/analysis/logit")

# Read in complete_st.csv
data <- read.csv("M:/senior living/data/psid data/complete_st.csv")

# Get a net worth variable measurement year
years <- c(1984, 1989, 1994, 1999, 2001, 2003, 2005, 2007, 2009, 2011)
data$measurementyr <- as.numeric(data$year %in% years)

# Get an age bucket variable
data$agebucket <- cut(data$age2, c(0, 15, 30, 45, 60, 75, 90, 105, 120))

# Make all dep vars dichotomous (0,1)
todum <- dummy(data$Trans_to)
occdum <- dummy(data$Housing.Category)
fromdum <- dummy(data$Trans_from)
data$moved[data$moved == 5] = 0
data <- cbind(data, todum, occdum, fromdum)

# Get factor variables for all RHS and LHS vars
#data$agebucket <- factor(data$agebucket)
#data$educ <- factor(data$educ)
#data$race <- factor(data$race)
#data$urban.rural.category <- factor(data$urban.rural.category)
#data$Trans_from <- factor(data$Trans_from)
#data$moved <- factor(data$moved)
#data$Trans_to <- factor(data$Trans_to)
#data$Housing.Category <- factor(data$Housing.Category)

# Run logits; save models
model1 <- glm(moved ~ agebucket+impwealth+educ+race+fromdum+urban.rural.category, 
	data=data, family="binomial", weights=indweight)




# Extract coefs 

# 