# This script contains tests for logit_by_hand.R 

# Source from logit_by_hand
dir <- "M:/senior living/code/senior-living/analysis/logit/logit_by_hand.R"
source(dir)

# Read in data
datadir <- "M:/senior living/data/psid data/complete_st.csv"
data <- read.csv(datadir)

# Gen age bucket var
edges <- c(0, 15, 30, 45, 60, 75, 90, 105, 125)
data <- getAgeBucket(data, edges)

# Define y (dependent variable)
data <- genDummies(c("Housing.Category"), data)
y.var <- "Housing.Category_SF"

# Define x (predictor variables)
x.labels <- c("agebucket", "Trans_to")

# Convert all variables in x.vars to dummies if they are categorical
max.level <- 10
dummies <- checkFactor(x.labels, data, max.level)
cont.x.vars <- unlist(dummies[1])
dummy.x.vars <- unlist(dummies[2])
cat.x.vars <- x.labels[!x.labels %in% cont.x.vars]
x.vars <- c(cont.x.vars, dummy.x.vars)

# Select beta starting values
betas <- c(1, rep(7, length(x.vars)))
betasList <- list("beta1"=)

# Get dummies and agebucket variable
data <- genDummies(cat.x.vars, data, max.level)

# Test calcLogLikelihood
x <- data.matrix(data[, x.vars])
y <- data.matrix(data[, y.var])
#llf1 <- calcLogLikelihood(betas, x, y)

# Run optim
model1 <- optim(betas, calcLogLikelihood, x=x, y=y, method="BFGS")