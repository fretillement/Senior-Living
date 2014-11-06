# This code runs a weighted logit model by hand with optim() on PSID data obtained from the get_complete script.
# See get_complete.py for more info

# Import libraries
library(dummies)
library(stats4)


genDummies <- function(varnames, data, max.level) { 
# Generates a set of dummies for each categorical var in varnames
# 
# Args: 
#   varnames: array of string w/ column names to be expanded to dummy
#   data: original dataframe
#
# Returns:  
#   data: original dataframe WITH dummy variables
#
# Error handling: 
  # Check that each varname is a categorical variable and has no null values
  for(v in varnames) {
    if (TRUE %in% is.na(data[, v])) {
      stop(paste(v, "has null values!"))
    }
  }
  data <- dummy.data.frame(names=varnames, data=data, sep="_")
  return(data)
}

checkFactor <- function(varnames, data, max.level) {
  cats <- character()
  orig <- character()
  for(v in varnames) { 
    if (length(unique(data[, v])) < max.level) {
      temp <- paste(v, "_", levels(factor(data[, v])), sep="")
      cats <- c(cats, temp)
    }
    else {
      orig <- c(orig, v)
    }
  }
  return(list(orig, cats))
}



getAgeBucket <- function(data, edges) { 
# Generates a age bucket var with boundaries at edges with age2
#
# Args: 
#   data: the original dataframe
#   edges: an array of integer boundaries at which to bin age2 values, e.g. (0, 15, 30, 45, ...)
#  
# Returns: 
#   data: the original dataframe WITH age bucket variable
#
# Error handling: 
# check whether any null/missing values are in age2
  if((TRUE %in% data$age2 > 107) || (TRUE %in% is.na(data$age2))) {
    stop("age2 has values >107 OR Null!")
  }  
  data$agebucket <- cut(data$age2, breaks=edges) 
  data$agebucket <- factor(data$agebucket)
  return(data)
}

CalcInvlogit <- function(x) {
# Computes the antilogit of a number x
#
# Args: 
# x is the linear regression model of the logit, e.g. 
# x = beta_0 + beta_1 * X_1 + beta_2 * X_2
# 
# Returns: 
# the inverse logit function for x. Used to calculate the 
# negative of log likelihood 
  invlogit <- 1 / (1+exp(-1 * x))
  return(invlogit)
}

calcLogLikelihood <- function(betas, x=x, y=y) { 
# Computes the negative log-likelihood 
#  
# Args: 
#   x: a dataframe of the predictor variables in the logit model 
#   y: a vector of the outcome variable (e.g. living in SF, etc)
#   betas: a vector of beta coefficients used in the logit model 
#  
# Return: 
#   llf: the negative log-likelihood value (to be minimized via MLE)
# 
# Error handling: 
  
  # Check if any values are null, and whether there are same number of coefficients as there are predictors
  if (TRUE %in% is.na(x) || TRUE %in% is.na(y)) {
    stop("There is one or more NA value in x and y!")
  }
  nbetas <- sapply(betas, length)
  if (length(nbetas)-1 != ncol(x)) {
    print(c(length(betas)-1, ncol(x)))
    stop(" Categorical vector and coef vector of different lengths!")
  }
  # Unpack betas  
  num.betas <- length(betas)
  for(i in seq(1, length(betas))) {
    assign(paste("beta", toString(i), sep=""), betas[i])
  }
  linsum <- beta1 + rowSums(unlist(mget(paste("beta", 2:num.betas, sep=""))) * x)
  p <- CalcInvlogit(linsum)
  llf <- -1 * sum(data$indweight * (y * log(p) + (1-y) * log(1-p)))
  return(llf)
}

minLogLikelihood <- function(betas, x, y) { 
# Minimizes a negative log likelihood function using maximum likelihood
#
# Args: 
#   x: a dataframe of the predictor variables in the logit model
#   y: a vector of the outcome variable
#   betas: a vector of beta coefficient "guesses" used in the logit model
#
# Return:
#   fit: an object of mle-class that contains coef estimates, fitted values, etc.
  fit <- mle(calcLogLikelihood, betas, x=x, y=y)
  return(fit)
}


# Set working directory 
#dir <- "M:/senior living/data/psid data/"
#setwd(dir)

# Read in the data 
#df <- read.csv("complete_st.csv")