require(stats4)
require(dummies)
require(plyr)

"
This script runs a logit model on PSID data. See getComplete.py for more information
on the PSID dataset 

The model coefficients, standard errors, z-score and p-values are all saved to csv

Dependencies: 
    logit.R: file with all functions required to implement a logit with optim() and get standard errors  
    housekeeping.R: contains functions required to clean up PSID file (complete_st.csv) before running logit
"

# Specify directories
#dirh <- "M:/senior living/code/senior-living/analysis/logit/housekeeping.R"
dirh <- "/Users/shruthivenkatesh/documents/senior living/senior-living/analysis/logit/housekeeping.R"
#dirl <- "M:/senior living/code/senior-living/analysis/logit/logit.R"
dirl <- "/Users/shruthivenkatesh/documents/senior living/senior-living/analysis/logit/logit.R"
#diro <- "M:/senior living/code/senior-living/analysis/logit/test.csv"
diro <- "/Users/shruthivenkateshdocuments/senior living/senior-living/analysis/logit/test.csv"
#dird <- "M:/senior living/data/Psid data/complete_st-logit.csv"
dird <- "/Users/shruthivenkatesh/documents/senior living/complete_st-logit.csv"

# Optional: source housekeeping.R; clean up and recode data if needed 
#source(dirh)

# Read in the data
data <- read.csv(dird)

# Get logit functions
source(dirl)

# Keep only observations for years with wealth vars with glm()
data <- data[data$year %in% c(seq(1984, 1994, 5), seq(1999, 2011, 2)), ]

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
           "urban.rural.code.Urban", "race2.Black", "race2.White", "impwealth")
yvar <- "trans_to.Senior"  
intercept <- data.frame(rep(1, nrow(data)))

x <- cbind(intercept, data[ , xvars])
y <- data[ , yvar]
x <- as.matrix(x)
y <- as.matrix(y)


#### Run logit f2 with only years with wealth and urban obs. 
modelf2 <- glm(f2, family=binomial(link = "logit"), data=data)
modelf2lm <- lm(f2, data=data)
betas <- array(modelf2$coefficients)

# with optim - unweighted
ufitf2 <- optim(betas, calcLogLikelihood, gr=logit.gr, x=x, y=y, method="BFGS", control=list(trace=TRUE, REPORT=1), hessian=TRUE)
ufitf2.res <- logit.summary(ufitf2)

# with optim - weighted
wfitf2 <- optim(betas, calcLogLikelihood, gr=logit.gr, x=x, y=y, method="BFGS", control=list(trace=TRUE, REPORT=1), hessian=TRUE)
wfitf2.res <- logit.summary(wfitf2)

#### Run logit f3 with only years with wealth and urban obs (interaction)




"
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
"