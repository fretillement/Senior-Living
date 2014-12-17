# Read the data
df <- read.csv("M:/alt_test.csv")


crosstabToFrom <- function(df) {
  # For a given age bucket, generate a weighted cross tab of transition to and from categories  
  #  
  # Args: 
  #    df: a PSID dataframe with agebucket variable
  #
  # Returns:    
  #    cross: a table with number of moves in each "to-from" pair (weight=indweight)
  cross <- xtabs(indweight ~ Trans_to_alt + Trans_from_alt, data=df)
}


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


# Generate age buckets
edges <- seq(18, 100, 5)
df <- getAgeBucket(df, edges)

# Make the cross tab
for(i in edges) {
    temp <- df[df$age2 %in% seq(i, i+4), ]  
    #temptab <- crosstabToFrom(temp)
    temptab <- table(temp$Trans_to_alt, temp$Trans_from_alt)
    write.table(temptab, file = "M:/alt_xtabs_counts.csv", append=TRUE, sep=",")
}  








# Write to csv