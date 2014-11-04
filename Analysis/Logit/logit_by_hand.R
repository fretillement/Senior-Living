# This code runs a logit model with only mle() on PSID data obtained from the get_complete script.

# Import libraries
library(dummies)
library(stats4)


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

calcLogLikelihood <- function(betas, x, y) { 
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
  if (TRUE %in% is.na(x) || TRUE %in% is.na(y)) {
    stop(" There is one or more NA value in x and y!")
  }
  if (length(betas[2:]) != length(x)) {
    print(c(length(betas[2:]), length(x)))
    stop(" Categorical vector and coef vector of different lengths!")
  }
  linsum <- betas[1] + sum(betas[2:length(betas)] * x)
  p <- calcInvlogit(linsum)
  llf <- -1 * sum(y * log(p) + (1-y) * log(1-p))
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
#   fit: an object of class mle-class that contains coef estimates, fitted values, etc.
  fit <- mle(calcLogLikelihood, start=betas, x=x, y=y)
  return(fit)
}


# Set working directory string
dir <- "M:/senior living/data/psid data/"


# Change directory 
setwd(dir)

# Read in the data 
#df <- read.csv("complete_st.csv")