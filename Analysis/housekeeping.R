require(plyr)
require(dummies)

# This script contains functions to prep PSID data for a logistic regression
# 
# For more information on the PSID data, see getComplete.py
#    
# For more information on the logistic regression implementation, see logit.R and runlogit1.R
#

# Set data and output directories
dird <- "M:/senior living/data/Psid data/complete_st.csv"
diro <- "M:/senior living/data/Psid data/complete_st-logit.csv"
  

getAgeBucket <- function(data, edges=seq(0,110,5)) { 
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
  #data$agebucket <- factor(data$agebucket)
  return(data)
}

checkFactor <- function(varnames, data, max.level) {
  # Checks whether each variable in varnames is a categorical variable
  #
  # Args: 
  #    varnames: array of string column names to be verified
  #    data: the original PSID dataframe
  #    max.level: the maximum number of unique values a var can take to be classified as categorical
  #  
  # Returns:  
  #    orig: vector of column names that are continuous vars
  #    cats: vector of categorical var column names  
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

fillInMoved <- function(data) {
# Fill in missing values of the variable moved
#  
# Args: 
#    data: complete PSID dataframe
#
# Returns: 
#    data: data with filled in missing values for moved
    data[(data$moved %in% c(5, 8, 9)), "moved"] <- 0
    return(data)  
}

fillInUrban <- function(data) {
# Fill in missing values of the variable urban.rural.code  
#  
# Args: 
#    data: complete PSID dataframe
#
# Returns: 
#    data: data with filled in missing values for moved
    data <- rename(data, c("urbanruralcode"= "urban.rural.code"))
    validyrs <- (data[, 'year'] >= 1984)
    urban <- (data[, 'urban.rural.code'] %in% seq(1,5))
    data[validyrs & urban, 'urban.rural.code'] <- "Urban"
    data[validyrs & !urban, 'urban.rural.code'] <- "Rural"
    #fill1984 <- function(group) {
    #    if((1984 %in% group$year) & (group[group$year == 1985, 'moved'] %in% c(5,0))) {
    #         group[group$year == 1984, 'urban.rural.code'] <- group[group$year == 1985, 'urban.rural.code']
    #    } 
    #   return(group)
    #}
    #data <- ddply(data, 'unique_pid', fill1984, .parallel=TRUE)        
    return(data)
}

fillInRace <- function(data) { 
# Recodes PSID original race variable to account for sparse reporting
#
# Args: 
#    data: complete PSID dataframe
#  
# Returns: 
#    output: original PSID dataframe with new variable, race2 for recoded race values
#
    white <- ((data$race == "White"))
    black <- ((data$race == "Black or African-American"))
    other <- !white & !black
    data[other, 'race2'] <- "NeitherRace"
    data[white, 'race2'] <- "White"
    data[black, 'race2'] <- "Black"
    return(data)
}

#####################################
## Implement houskeeping functions ##
#####################################
if(interactive()) {
    # Read in data
    data <- read.csv(dird)
    
    # Keep ONLY observations for ages >= min.age
    min.age <- 55
    data <- data[((data$age2 >= min.age)), ]
  
    #Clean up urban.rural.code, moved, and race variables
    data <- fillInUrban(data)
    data <- fillInMoved(data)
    data <- fillInRace(data)
    
    # Generate dummies from independent variables: 
    # agebucket, Trans_from, urban status, moved, race, housing category, marital status, 
    # period indicator (1984-1995 and 1996-2011)
    edges <- seq(min.age, 110, 5)
    data <- getAgeBucket(data, edges)
    agebucketdum <- data.frame(dummy(data$agebucket))
    agebucketdum <- setNames(agebucketdum, paste("agebucket.", edges, sep=""))
    transfromdum <- data.frame(dummy(data$Trans_from))
    movedum <- data.frame(dummy(data$moved))
    urbandum <- data.frame(dummy(data$urban.rural.code))
    urbandum <- urbandum[, c("urban.rural.code.Rural", 'urban.rural.code.Urban')]
    racedum <- data.frame(dummy(data$race2))
    hcatdum <- data.frame(dummy(data$Housing.Category))
    mardum <- data.frame(dummy(data$mar))
    data$period <- as.numeric(data$year %in% seq(1984, 2001))
    perioddum <- data.frame(dummy(data$period))
    colnames(perioddum) <- c("period.2001-2011", "period.1984-2001")
    data <- cbind(data, agebucketdum, transfromdum, movedum, urbandum, racedum, hcatdum,
                  mardum, perioddum)
    
    # Dependent variable: to_senior
    transtodum <- data.frame(dummy(data$Trans_to))
    data <- cbind(data, transtodum)
    
    ### Save the data ### 
    #write.csv(data, diro, row.names=FALSE)
}
