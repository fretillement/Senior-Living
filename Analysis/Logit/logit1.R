library(dummies)

"
This script runs logit models on the cleaned, most recent stacked
version of complete_st.csv. 

Complete_st.csv is built by getComplete.py. See that file for more info
"

#### Change wd and read complete_st.csv
setwd("M:/Senior living/code/senior-living/analysis/logit/")
data = read.csv("M:/senior living/data/psid data/complete_st.csv")

#### Generate dummy variables for transition and occupancy 
occdum <- dummy(data$Housing.Category)
fromdum <- dummy(data$Trans_from)
todum <- dummy(data$Trans_to)
data$moved[(data$moved == 5) | (data$moved == 9) | (data$moved == 8)] = 0
drops <- c("Trans_to0", "Trans_from0", "X", "Unnamed..0")
data <- cbind(data, todum, occdum, fromdum)
data <- data[, !(names(data) %in% drops)]

#### Generate age bucket variable; declare as categorical
data$agebucket = cut(data$age2, c(0, 15, 30, 45, 60, 75, 90, 105, 125))
xtabs(~year+agebucket, data)
data$agebucket = factor(data$agebucket)

#### Clean up dependent vars: educ
data$educ[data$educ > 17] = 0

#### Run logits; save models
wealthyrs <- c(1984, 1989, 1994, 1999, 2001,2003, 2005, 2007, 2009, 2011)
# Set 1 Transitions: no impwealth
m.moved <- glm(moved ~ agebucket+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
	data=data, family=binomial(link="logit"))
write.csv(summary.glm(m.moved)$coefficients, "moved.csv")

m.movedSF <- glm(Trans_toSF ~ agebucket+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
                 data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.movedSF)$coefficients, "movedSF.csv")

m.movedMF <- glm(Trans_toMF ~ agebucket+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
                 data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.movedMF)$coefficients, "movedMF.csv")

m.movedShared <- glm(Trans_toShared ~ agebucket+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
                     data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.movedShared)$coefficients, "movedShared.csv")

m.movedSenior <- glm(Trans_toSenior ~ agebucket+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
                     data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.movedSenior)$coefficients, "movedSenior.csv")

# Set 2 Transitions: WITH impwealth
m.wmoved <- glm(moved ~ agebucket+impwealth+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
                data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wmoved)$coefficients, "wmoved.csv")


m.wmovedSF <- glm(Trans_toSF ~ agebucket+impwealth+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
               data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wmovedSF)$coefficients, "wmovedSF.csv")

m.wmovedMF <- glm(Trans_toMF ~ agebucket+impwealth+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
               data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wmovedMF)$coefficients, "wmovedMF.csv")

m.wmovedShared <- glm(Trans_toShared ~ agebucket+impwealth+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
    data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wmovedShared)$coefficients, "wmovedShared.csv")

m.wmovedSenior <- glm(Trans_toSenior ~ agebucket+impwealth+educ+race+Trans_fromMF+Trans_fromOther+Trans_fromSenior+Trans_fromSF+Trans_fromShared+urban.rural.category, 
    data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wmovedSenior)$coefficients, "wmovedSenior.csv")

# Set 3 Occupancy: without wealth
m.occ <- glm(Housing.Category ~ agebucket+educ+race+urban.rural.category, 
               data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.occ)$coefficients, "occ.csv")

m.occSF <- glm(Housing.CategorySF ~ agebucket+educ+race+urban.rural.category,
               data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.occSF)$coefficients, "occSF.csv")

m.occMF <- glm(Housing.CategoryMF ~ agebucket+educ+race+urban.rural.category,
               data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.occNF)$coefficients, "occMF.csv")

m.occShared <- glm(Housing.CategoryShared ~ agebucket+educ+race+urban.rural.category,
                   data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.occShared)$coefficients, "occShared.csv")

m.occSenior <- glm(Housing.CategorySenior ~ agebucket+educ+race+urban.rural.category,
                   data=data, family=binomial, weights=indweight)
write.csv(summary.glm(m.occSenior)$coefficients, "occSenior.csv")

# Set 4 Occupancy: WITH wealth
m.wocc <- glm(Housing.Category ~ agebucket+impwealth+educ+race+urban.rural.category, 
              data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.wocc)$coefficients, "wocc.csv")

m.woccSF <- glm(Housing.CategorySF ~ agebucket+impwealth+educ+race+urban.rural.category,
                data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.woccSF)$coefficients, "woccSF.csv")

m.woccMF <- glm(Housing.CategoryMF ~ agebucket+impwealth+educ+race+urban.rural.category,
                data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.woccMF)$coefficients, "woccMF.csv")

m.woccShared <- glm(Housing.CategoryShared ~ agebucket+impwealth+educ+race+urban.rural.category,
                    data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.woccShared)$coefficients, "woccShared.csv")

m.woccSenior <- glm(Housing.CategorySenior ~ agebucket+impwealth+educ+race+urban.rural.category,
                    data=data[data$year %in% wealthyrs,], family=binomial, weights=indweight)
write.csv(summary.glm(m.woccSenior)$coefficients, "woccSenior.csv")

#### Extract coefs / summary and write to csv for each model 
#def write(glm.model, ): 
# return

