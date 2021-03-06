require(dummies)
require(plyr)
require(stargazer)

"
This script runs a baseline regression for senior living occupancy
using PSID data 
"
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
  #data$agebucket <- factor(data$agebucket)
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
    data <- rename(data, c("urban.rural.Category" = "urban.rural.code"))
    validyrs <- data$year >= 1984
    urban <- (data$urban.rural.code %in% seq(1,5))
    data[validyrs & urban, 'urban.rural.code'] <- "Urban"
    data[validyrs & !urban, 'urban.rural.code'] <- "Rural"
    #data$urban.rural.code <- droplevels(data$urban.rural.code)
    #fill1984 <- function(group) {
    #   if((1985 %in% group$year) & (1984 %in% group$year)){
    #        if(group[group$year == 1985, 'moved'] %in% c(5, 0, 8, 9)) {
    #            group[group$year == 1984, 'urban.rural.code'] <- group[group$year == 1985, 'urban.rural.code']
    #        }   
    #    }
    #    return(group)    
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


# Read in the data
df <- read.csv("M:/Senior living/Data/psid data/complete_st.csv")

# Drop all ages < 55
df <- df[(df$age2 >= 55), ]

# Drop all years without wealth measurement 
wmeasured <- c(1984, 1989, 1994, seq(1999, 2011, 2))
df <- df[(df$year %in% wmeasured), ]

# Generate the wealth quintile
df$wealthq <- as.integer(cut(df$impwealth, quantile(df$impwealth, include.lowest = TRUE)))
df <- df[!is.na(df$wealthq), ]

# Gen age buckets
edges1 <- seq(55, 110, 5)
df$agebucket <- cut(df$age2, breaks=edges1, include.lowest=TRUE)
df$agebucket <- droplevels(df$agebucket)

# Fill in Race and Urban
df <- fillInRace(df)
df <- fillInUrban(df)

# Fix educ var
df[df$educ > 17, 'educ'] <- 0

# Generate dummies
# Age
agebucketdum <- data.frame(dummy(df$agebucket))
agebucketdum <- setNames(agebucketdum, paste("agebucket.", edges1[1 : length(edges1)-1], sep=""))

# Urban
urbandum <- data.frame(dummy(df$urban.rural.code))
urbandum <- urbandum[, c("urban.rural.code.Rural", 'urban.rural.code.Urban')]

# Race
racedum <- data.frame(dummy(df$race2))

# Marital
mardum <- data.frame(dummy(df$mar))

# Housing category (occupancy)
hcatdum <- data.frame(dummy(df$Housing.Category))

# Wealth quintile
wealthqdum <- data.frame(dummy(df$wealthq))

# Period dummies
df$post.1995 <- as.integer(df$year >= 1995)
df$post.1985 <- as.integer(df$year >= 1985)


# Attach dummies to df
df <- cbind(df, agebucketdum, urbandum, racedum, hcatdum, mardum, wealthqdum)
#df <- cbind(df, agebucketdum, urbandum, racedum, hcatdum, mardum)

# Create a separate category for ages 95+ 
df$agebucket.95plus <- as.integer(df$agebucket.95 | df$agebucket.100 | df$agebucket.105)

# DUmmy for college ed
df$college <- as.integer(df$educ >= 12)


#############################
## Run logits on occupancy ##
#############################
# Run logit on OCCUPANCY FOR 55 + 
f1 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + agebucket.100 + agebucket.105 +
      mar.Married + 
      race2.White + 
      race2.Black + 
      wealthq + 
      urban.rural.code.Urban + 
      educ

model.f1 <- glm(f1, family = binomial(link = "logit"), data = df)


# Occupancy for 55+, wealthq dummies 
f2 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
      mar.Married + 
      race2.White + 
      race2.Black + 
      urban.rural.code.Urban +
      wealthq.2 + 
      wealthq.3 + 
      wealthq.4 +
      educ
modelf2 <- glm(f2, family = binomial(link = "logit"), data = df)
stargazer(modelf2, 
          type = "latex",
          font.size = "normalsize",
          no.space = TRUE,
          #type = "text",
          header = TRUE,
          out.header = TRUE,
          dep.var.labels.include = FALSE,
          column.labels = c("Occupancy in Seniors Housing"),
          covariate.labels = c("Age group 60-64", "Age group 65-69", "Age group 70-74", "Age group 75-79", "Age group 80-84", "Age group 85-89", "Age group 90-94", "Age group 95+", "Married", "White", "Black", "Urban", "Wealth quartile 2", "Wealth quartile 3", "Wealth quartile 4", "Education level"), 
          notes.append = TRUE, 
          notes = c("Standard errors in parentheses"),
          title = c("Table 1"), 
          out = "M:/table1.tex")



# Occupancy for 55+, wealthq dummies, period dummies interacted w/ ALL variables in f2
f3 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
                                        mar.Married + 
                                        race2.White + 
                                        race2.Black + 
                                        urban.rural.code.Urban +
                                        wealthq.2 + 
                                        wealthq.3 + 
                                        wealthq.4 +
                                        educ +
                                        post.1995:agebucket.60 + agebucket.65:post.1995 + agebucket.70:post.1995 + agebucket.75:post.1995 +
                                        agebucket.80:post.1995 + agebucket.85:post.1995 + agebucket.90:post.1995 + 
                                        agebucket.95plus:post.1995 + 
                                        mar.Married:post.1995 +
                                        race2.White:post.1995 + 
                                        race2.Black:post.1995 + 
                                        urban.rural.code.Urban:post.1995 + 
                                        wealthq.2:post.1995 + 
                                        wealthq.3:post.1995 + 
                                        wealthq.4:post.1995 + 
                                        educ:post.1995
modelf3 <- glm(f3, family = binomial(link = "logit"), data = df)
stargazer(modelf3,           
          type = "latex",
          font.size = "normalsize",
          no.space = TRUE,
          #type = "text",
          header = TRUE,
          out.header = TRUE,
          dep.var.labels.include = FALSE,
          column.labels = c("Occupancy in Seniors Housing"),
          covariate.labels = c("Age group 60-64", "Age group 65-69", "Age group 70-74", "Age group 75-79", "Age group 80-84", "Age group 85-89", "Age group 90-94", "Age group 95+", "Married", "White", "Black", "Urban", "Wealth quartile 2", "Wealth quartile 3", "Wealth quartile 4", "Education level",
                               "Age group 60-64 * Post-1995", "Age group 65-69 * Post-1995", "Age group 70-74 * Post-1995", "Age group 75-79 * Post-1995", "Age group 80-84 * Post-1995", "Age group 85-89 * Post-1995", "Age group 90-94 * Post-1995", "Age group 95+ * Post-1995",
                               "Married * Post-1995", "White * Post-1995", "Black * Post-1995", "Urban * Post-1995", "Wealth quartile 2 * Post-1995", "Wealth quartile 3 * Post-1995", "Wealth quartile 4 * Post-1995", "Education level * Post-1995"), 
          notes.append = TRUE, 
          notes = c("Standard errors in parentheses"),
          title = c("Table 4"), 
          out = "M:/table4.tex")




# Occupancy for 55+; dummy for wealthq.4 interacted with agebuckets
f4 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
      mar.Married + 
      race2.White + 
      race2.Black + 
      urban.rural.code.Urban +
      educ + 
      #wealthq.2 + wealthq.3 + wealthq.4 + 
      wealthq.4:agebucket.60 + wealthq.4:agebucket.65 + wealthq.4:agebucket.70 + wealthq.4:agebucket.75 +
      wealthq.4:agebucket.80 + wealthq.4:agebucket.85 + wealthq.4:agebucket.90 + wealthq.4:agebucket.95plus
modelf4 <- glm(f4, family = binomial(link = "logit"), data = df) 
stargazer(modelf4, 
          font.size = "normalsize",
          type = "latex",
          header = TRUE,
          out.header = TRUE,
          dep.var.labels.include = FALSE,
          column.labels = c("Occupancy in Seniors Housing"),
          covariate.labels = c("Age group 60-64", "Age group 65-69", "Age group 70-74", "Age group 75-79", "Age group 80-84", "Age group 85-89", "Age group 90-94", "Age group 95+", "Married", "White", "Black", "Urban", "Education level",
                               "Age group 60-64 * Top wealth quartile", "Age group 65-69 * Top wealth quartile", "Age group 70-74 * Top wealth quartile", "Age group 75-79 * Top wealth quartile", "Age group 80-84 * Top wealth quartile", "Age group 85-89 * Top wealth quartile", 
                               "Age group 90-94 * Top wealth quartile", "Age group 95+ * Top wealth quartile"), 
          notes.append = TRUE, 
          notes = c("Standard errors in parentheses"),
          title = c("Table 2"),
          no.space = TRUE,
          out = "M:/table2.tex")





# Occupancy for 55+; adding agebucket * impwealth * period.1995 dummy 
f5 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
                                        mar.Married + 
                                        race2.White + 
                                        race2.Black + 
                                        urban.rural.code.Urban +
                                        educ + 
                                        #wealthq.2 + wealthq.3 + wealthq.4 + 
                                        wealthq.4:agebucket.60:post.1995 + wealthq.4:agebucket.65:post.1995 + wealthq.4:agebucket.70:post.1995 +
                                        wealthq.4:agebucket.75:post.1995 + wealthq.4:agebucket.80:post.1995 + wealthq.4:agebucket.85:post.1995 +
                                        wealthq.4:agebucket.90:post.1995 + wealthq.4:agebucket.95plus:post.1995 
modelf5 <- glm(f5, family = binomial(link = "logit"), data = df)                                        
stargazer(modelf5, 
          font.size = "normalsize",
          type = "latex",
          header = FALSE,
          out.header = TRUE,
          dep.var.labels.include = FALSE,
          column.labels = c("Occupancy in Seniors Housing"),
          covariate.labels = c("Age group 60-64", "Age group 65-69", "Age group 70-74", "Age group 75-79", "Age group 80-84", "Age group 85-89", "Age group 90-94", "Age group 95+", "Married", "White", "Black", "Urban", "Education level",
                               "Age group 60-64 * Top wealth quartile * Post-1995", "Age group 65-69 * Top wealth quartile * Post-1995", "Age group 70-74 * Top wealth quartile * Post-1995", "Age group 75-79 * Top wealth quartile * Post-1995", 
                               "Age group 80-84 * Top wealth quartile * Post-1995", "Age group 85-89 * Top wealth quartile * Post-1995", 
                               "Age group 90-94 * Top wealth quartile * Post-1995", "Age group 95+ * Top wealth quartile * Post-1995"), 
          notes.append = TRUE, 
          notes = c("Standard errors in parentheses"),
          no.space = TRUE,
          out = "M:/table3.tex")






# Occupancy of 55+; all years 1968-2011; leave out wealth, urban vars
f6 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
                                        mar.Married + 
                                        race2.White + 
                                        race2.Black + 
                                        educ
modelf6 <- glm(f6, family = binomial(link = "logit"), data = df)


# Occupancy of 55+; all years 1968-2011; leave out wealth, urban vars; include interaction b/w
f7 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95plus + 
                                        mar.Married + 
                                        race2.White + 
                                        race2.Black + 
                                        educ + 
                                        agebucket.60:college:post.1985 + agebucket.65:college:post.1985 + agebucket.70:college:post.1985 +
                                        agebucket.75:college:post.1985 + agebucket.80:college:post.1985 + agebucket.85:college:post.1985 +
                                        agebucket.90:college:post.1985 + agebucket.95plus:college:post.1985
modelf7 <- glm(f7, family = binomial(link = "logit"), data = df)

"
# Run logit on OCCUPANCY for 65 +
f2 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + agebucket.100 + agebucket.105 +
     mar.Married + 
     race2.White + 
     race2.Black + 
     wealthq + 
     urban.rural.code.Urban + 
     educ

model.f2 <- glm(f1, family=binomial(link="logit"), data=df[df$age2 >= 65, ])

# Run logit on housing occupancy for 55+, but with 75/25 wealth breakdown
df$wealthtop25 <- df$wealthq > 3
f3 <- Housing.Category.Senior.housing ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 + agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + agebucket.100 + agebucket.105 +
  mar.Married + 
  race2.White + 
  race2.Black + 
  wealthtop25 + 
  urban.rural.code.Urban + 
  educ

model.f3 <- glm(f3, family=binomial(link="logit"), data=df)
"
