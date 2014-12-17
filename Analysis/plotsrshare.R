require(plyr)


# Read in the data
df65 <- read.csv('M:/senior living/data/psid data/complete_st.csv')

# Clean 

# Keep 65 and older only
df65 <- df65[df65$age2 >= 65, ]

# Generate age buckets
edges65 <- c(seq(65, 84, 10), 85, 107)
df65$agebucketv1 <- cut(df65$age2, edges65, include.lowest = TRUE)

# Calculate the share of senior in each agebucket for each year from 1984-onward
inSrHousing <- function(agedf) {
    tot <- sum(agedf$indweight)  
    insr <- sum( (agedf$Housing.Category == 'Senior housing') %*% agedf$indweight)
    return(insr/tot)
}

# For a given year, break down into the four age categories 
bucketsInSr <- function(yeardf) { 
    plus65 <- yeardf
    df65to75 <- yeardf[yeardf$agebucketv1 == "[65,75]", ]
    df76to85 <- yeardf[yeardf$agebucketv1 == "(75,85]", ]
    df86plus <- yeardf[yeardf$agebucketv1 == "(85,107]", ]
    
    df65to75$agebucketv1 <- droplevels(df65to75$agebucketv1)
    df76to85$agebucketv1 <- droplevels(df76to85$agebucketv1)
    df86plus$agebucketv1 <- droplevels(df86plus$agebucketv1)
  
    overall <- inSrHousing(plus65)
    age1 <- inSrHousing(df65to75)
    age2 <- inSrHousing(df76to85)
    age3 <- inSrHousing(df86plus)
  
    output <- data.frame('65plus' = overall, '65-75' = age1, '76-85' = age2, '86plus' = age3)    
}

# Apply the above functions
yearshares <- ddply(df65, 'year', .fun = bucketsInSr, .parallel = TRUE)
yearshares <- rename(yearshares, c("X65plus" = "65plus", "X65.75" = "65-75", "X76.85" = "76-85", "X86plus" = "86plus"))
write.csv(yearshares, "M:/test.csv", row.names = FALSE)



