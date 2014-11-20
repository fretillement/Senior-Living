require(foreign)
require(ggplot)
require(nnet)
require(dummies)

dir <- "M:/senior living/code/senior-living/analysis/logit/logit_by_hand.R"
source(dir)


# Read the data
datadir <- "M:/senior living/data/psid data/complete_st.csv"
data <- read.csv(datadir)

# Gen age bucket var
edges <- c(0, 15, 30, 45, 60, 75, 90, 105, 125)
data <- getAgeBucket(data, edges)

# Get dummy for age buckets
data$agebucket <- as.integer(factor(data$agebucket))
ages <- dummy(data$agebucket)
data <- cbind(data, ages)

# Get gender dummy 
gender <- dummy(data$gender)
data <- cbind(data, gender)

# Get racial dummies
race <- dummy(data$race)
data <- cbind(data, race)

# Get marital dummies
married <- dummy(data$mar)
data <- cbind(data, married)

# Get urbanicity variable
data$urban = data$urban.rural.code <= 5

# Run the model
data$Housing.Category2 <- relevel(data$Housing.Category, ref="Other")
model1 <- multinom(Housing.Category2 ~ agebucket2 + agebucket3 + agebucket4 + agebucket5 + agebucket6 + agebucket7 + agebucket8 + genderFemale + raceAsian + raceOther + raceWhite + marMarried + urban, data=data)  

summary.model1 <- summary(model1)
write.csv( summary.model1$coefficients, "M:/test_model2.csv")
write.csv( summary.model1$standard.errors, "M:/test_model2se.csv")


# Calculate p-value from standard errors
z <- summary(model1)$coefficients/summary(model1)$standard.errors

p <- (1-pnorm(abs(z), 0, 1)) * 2
