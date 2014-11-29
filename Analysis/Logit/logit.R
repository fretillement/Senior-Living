require(stats4)

# This code contains functions needed to run a WEIGHTED logistic regression with optim() 
#
# It uses PSID data obtained from the get_complete script.
# See get_complete.py for more info about the raw PSID data
# See testlogit.R for test code and implementation
#


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
#   x: a matrix of the predictor variables in the logit model
#      NOTE: the first column MUST be a vector of 1's for the intercept!!!
#   y: a matrix of the outcome variable (e.g. living in SF, etc)
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
  if (length(nbetas) != ncol(x)) {
    print(c(length(betas), ncol(x)))
    stop(" Categorical vector and coef vector of different lengths!")
  }
  w <- as.matrix(data$indweight)
  exprob <- exp(x %*% betas)
  prob <- exprob / (1 + exprob)
  logprob <- log(prob)
  
  y0 <- 1 - y
  exprob0 <- log(1 - prob)
  
  y0t <- t(y0)
  yt <- t(y)
  wt <- t(w)
   
  llf <- -sum((wt * yt) %*% logprob + (wt * y0t) %*% exprob0)
  # Unpack betas  
  #num.betas <- length(betas)
  #for(i in seq(1, length(betas))) {
  #  assign(paste("beta", toString(i), sep=""), betas[i])
  #}
  #linsum <- beta1 + rowSums(unlist(mget(paste("beta", 2:num.betas, sep=""))) * x)
  #p <- CalcInvlogit(linsum)
  #llf <- -1 * sum(data$indweight * (y * log(p) + (1-y) * log(1-p)))
  return(llf)
}

minLogLikelihood <- function(betas, x, y) { 
# Minimizes a negative log likelihood function using optim
#
# Args: 
#   x: a dataframe of the predictor variables in the logit model
#   y: a vector of the outcome variable
#   betas: a vector of beta coefficient "guesses" used in the logit model
#
# Return:
#   fit: an object of mle-class that contains coef estimates, fitted values, etc.
  fit <- optim(calcLogLikelihood, betas, x=x, y=y, method="BFGS")
  return(fit)
}

logit.gr <- function(betas, x, y) {
# Calculates the logit gradient (used to calculate standard errors)  
#
# Args: 
#    betas: 
    x <- as.matrix(x)
    y <- as.matrix(y)
    gradient <- betas * 0    
    exprob <- exp(x %*% betas) 
    prob1 <- exprob / (1+exprob) 
    
    for (k in 1:ncol(x)) { 
      gradient[k] <- sum(x[, k] * (y - prob1))
    }
    return(-gradient)
}

