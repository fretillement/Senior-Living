require(stats4)
require(dummies)
require(plyr)

"
This script runs a logit model on PSID data. See getComplete.py for more information
on the PSID dataset 

The model is as follows: 

Standard error and beta values are 


Dependencies: 
    logit.R: file with all functions required to implement a logit with optim() 
    housekeeping.R: contains functions required to clean up PSID before running logit
"

# Specify directories
dirh <- "M:/senior living/code/senior-living/analysis/logit/housekeeping.R"
dirl <- "M:/senior living/code/senior-living/analysis/logit/logit.R"
diro <- "M:/senior living/code/senior-living/analysis/logit/test.csv"
dird <- "M:/senior living/data/Psid data/complete_st.csv"

# Source housekeeping and logit functions
source(dirh)
source(dirl)

# Read in data
data <- read.csv(dird)

# Keep ONLY observations for ages >= min.age
min.age <- 55
data <- data[((data$age >= min.age)), ]

#Clean up moved, urban variable
data <- fillInUrban(data)
data <- fillInMoved(data)
data <- fillInRace(data)

# Generate dummies from independent variables: 
# agebucket, Trans_from, urban status, moved, race 
edges <- seq(min.age, 110, 5)
data <- getAgeBucket(data, edges)
agebucketdum <- data.frame(dummy(data$agebucket))
agebucketdum <- setNames(agebucketdum, paste("agebucket.", edges, sep=""))
transfromdum <- data.frame(dummy(data$trans_from))
movedum <- data.frame(dummy(data$moved))
urbandum <- data.frame(dummy(data$urban.rural.code))
urbandum <- urbandum[, c("urban.rural.code.Rural", 'urban.rural.code.Urban')]
racedum <- data.frame(dummy(data$race2))
data <- cbind(data, agebucketdum, transfromdum, movedum, urbandum, racedum)


# Dependent variable: to_senior
transtodum <- data.frame(dummy(data$trans_to))
data <- cbind(data, transtodum)
### Save the data ### 
write.csv(data, "M:/senior living/data/Psid data/complete_st-logit.csv", row.names=FALSE)


# Set up formula, x and y matrices for logistic regressions
f1 <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
                        agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
                        agebucket.100 + agebucket.105 +
                        trans_from.SF + trans_from.Shared + 
                        urban.rural.code.Urban + 
                        race2.Black + race2.White 

f2 <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
                        agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
                        agebucket.100 + agebucket.105 +
                        trans_from.SF + trans_from.Shared + 
                        urban.rural.code.Urban + 
                        race2.Black + race2.White + 
                        impwealth


xvars <- c(paste("agebucket.", seq(60, 105, 5), sep=""), "trans_from.SF", "trans_from.Shared", 
           "urban.rural.code.Urban", "race2.Black", "race2.White")
yvar <- "trans_to.Senior"  
intercept <- data.frame(rep(1, nrow(data)))

x <- cbind(intercept, data[ , xvars])
y <- data[ , yvar]
betas <- c(-7, rep(1, length(xvars)))

x <- as.matrix(x)
y <- as.matrix(y)


#### Run an UNWEIGHTED logit with only years with wealth and urban obs. 
# Keep only observations for years with wealth vars
data <- data[data$year %in% c(seq(1984, 1994, 5), seq(1999, 2011, 2)), ]

# Keep only observations for urban.rural.code values != 0 
data <- data[data$urban.rural.code != 0, ]

# with glm 

# with optim only 


#### Run an UNWEIGHTED logit with glm()
modelf1 <- glm(f1, family=binomial(link = "logit"), data=data)

#### Run WEIGHTED logit w/ logit.R and optim()
fitf1 <- optim(modelf1$coefficients, calcLogLikelihood, x=x, y=y, method="BFGS")

#### Run an UNWEIGHTED logit with optim()
modelu1 <- optim(betas, calcLogLikelihood, gr=logit.gr, x=x, y=y, method="BFGS", control=list(trace=TRUE, REPORT=1), hessian=TRUE)
coeffs <- modelu1$par
covmat <- solve(modelu1$hessian)
stderr <- sqrt(diag(covmat))
zscore <- coeffs/stderr
pvalue <- 2*(1 - pnorm(abs(zscore)))
results <- cbind(coeffs, stderr, zscore, pvalue)
colnames(results) <- c("Coeff.", "Std. Err.", "z", "p value")
print(results)  

#### Run a WEIGHTED logit with optim()
modelw1 <- optim(betas, calcLogLikelihood, gr=logit.gr, x=x, y=y, method="BFGS", control=list(trace=TRUE, REPORT=1), hessian=TRUE)
coeffs <- modelw1$par
covmat <- solve(modelw1$hessian)
stderr <- sqrt(diag(covmat))
zscore <- coeffs/stderr
pvalue <- 2*(1 - pnorm(abs(zscore)))
results <- cbind(coeffs, stderr, zscore, pvalue)
colnames(results) <- c("Coeff.", "Std. Err.", "z", "p value")
print(results)  


