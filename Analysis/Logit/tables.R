require(stargazer)
require(plyr)
require(matrixStats)
require(ggplot2)
require(reshape2)
require(lmtest)

# This script generates the tables and charts in latex on elderly 
# housing choice measured by the PSID. 
#
# For more information about the data, see get_complete.py
#
# Dependencies: crosstabs.R, logit.R
#

# Set directories
#dird.55plus <- "M:/senior living/data/Psid data/complete_st-logit.csv"
dird.55plus <- "/users/shruthivenkatesh/documents/senior living/complete_st-logit.csv"
dird.complete <- "M:/senior living/data/psid data/complete_st.csv"
dirh <-  "M:/senior living/code/senior-living/analysis/logit/housekeeping.R"
dir.xtabs <- "M:/senior living/code/senior-living/analysis/Crosstabs/xtabs.R"
dir.xtabsdata <- "M:/senior living/data/psid data/tosr_share.csv"
dir.xtabsdata2 <- "/users/shruthivenkatesh/documents/senior living/senior-living/"
dir.logit <- "/users/shruthivenkatesh/documents/senior living/senior-living/analysis/logit/logit.R"
# Optional: Clean up if necessary
#source(dirh)


##########################################
## Table 1: Generate summary statistics ##
##########################################
# Read in data 
data <- read.csv(dird.55plus)

# Select variables to summarize
select <- c('age2', 'mar', 'moved2', 'impwealth', 'urban.rural.code',
            'trans_to.Senior', 'trans_to.MF', 'trans_to.SF', 'trans_to.Shared',
            'race2.White', 'race2.Black', 'race2.Neither',
            'trans_from.Senior', 'trans_from.MF', 'trans_from.SF', 'trans_from.Shared',
            'housingcategory.Senior', 'housingcategory.MF', 'housingcategory.SF', 'housingcategory.Shared')

select.lab <- c("Age",
                "1 if married",
                "1 if moved from previous year",
                "Reported net wealth",
                "1 if respondent lives in an urban area",                 
                "1 if respondent has moved to a senior living facility in the past year",
                "1 if respondent has moved to a multifamily unit in the past year",
                "1 if respondent has moved to a single family home in the past year",
                "1 if respondent has moved to a shared home with other family in the past year",                
                "1 if respondent is White",
                "1 if respondent is Black or African-American",
                "1 if respondent reports a race apart from White, Black, or African-American",                 
                "1 if respondent has moved from a senior living facility in the past year",
                "1 if respondent has moved from a multifamily unit in the past year",
                "1 if respondent has moved from a single family home in the past year",
                "1 if respondent has moved from a shared home with other family in the past year",
                "1 if respondent resides in a senior living facility", 
                "1 if respondent resides in a multifamily housing unit",
                "1 if respondent resides in a single family home", 
                "1 if respondent lives in a shared home with other family")

data.sum <- data[, select]
data.sum[, 'urban.rural.code'] <- as.numeric(factor(data.sum$urban.rural.code))
data.sum$mar <- as.numeric(factor(data.sum$mar))
select.mean <- round(colMeans(data.sum), digits=3)
select.sd <- round(colSds(as.matrix(data.sum)), digits=3)

t1 <- data.frame(cbind(select, select.lab, select.mean, select.sd))
t1$select.mean <- as.numeric(t1$select.mean)
t1$select.sd <- as.numeric(t1$select.sd)

is.num <- sapply(t1, is.numeric)
t1[is.num] <- lapply(t1[is.num], round, 2)

stargazer(t1, 
          type = "latex",
          summary = FALSE,
          title = "Summary of Select PSID Variables, 1984-2011",
          out = "M:/test.tex",
          out.header = TRUE,
          column.labels <- c("Variable Name", "Description", "Mean", "Standard Deviaton"),
          align = TRUE,
          digits = 3,
          float.env = 'sidewaystable',
          float = TRUE,
          table.placement = "t")

#########################################
## Table 2: Hazard rates by age bucket ##
#########################################
data <- read.csv("M:/senior living/data/psid data/hazardrates.csv")
data <- data[!(data$agebucket %in% c("(100,105]", "(105,110]", "(90,95]", "(95,100]")),  ]
data <- rename(data, c("Age bucket" = "Age Group", "X1968.2011"= "1968-2011", "X1968.1984"="1968-1984", "X1985.1995"="1985-1995", "X1996.2011"="1996-2011"))
stargazer(data,
          type="latex",
          summary=FALSE,
          title="Mobility Rates by Age Group, PSID 1968-2011", 
          digits = 3, 
          dep.var.labels = c("1968-2011", "1968-1984", "1985-1995", "1996-2011"),
          out.header = TRUE,
          dep.var.caption = c("Time period"),
          rownames = FALSE,
          label = c("Table 2"),
          out="M:/test.tex")

##############################################
## Table 3: Crosstabs to/from by age bucket ##
##############################################
source(dir.xtabs)
data <- read.csv(dird.55plus)
data <- data[(data$trans_from != 0) & (data$trans_to != 0), ]
data$trans_from <- droplevels(data$trans_from)
data$trans_to <- droplevels(data$trans_to)
t1 <- crosstabToFrom(data)


###########################################################
## Chart 1: incr. in moves to senior between periods 1-3 ##
###########################################################
data <- read.csv(dir.xtabsdata)
data <- data[!is.na(data$agebucket) & !(data$agebucket %in% c("(85,90]", "(95,100]", "(90,95]")), ]
data <- rename(data, c("X1968.2011"="1968-2011", "X1968.1984"="1968-1984", "X1985.1995"="1985-1995", "X1996.2011"="1996-2011"))

#source(dir.xtabs)

m1 <- melt(data, idvars=c("agebucket"), variable.name="time.period", value.name="toSL.share")

p1 <- ggplot(m1, aes(x=agebucket, y=toSL.share, col=time.period, group=time.period, line=20)) + geom_line(size=1.5)
p1 <- p1 + labs(x="Age group",
             y="Moves to senior housing from single family and shared homes as share of total moves",
             title="Moves to Senior Housing as a Fraction of Total Transitions") 
p1 <- p1 + scale_color_discrete("Time Period") + theme_bw(base_size = 14, base_family="Helvetica")
p1 <- p1 + theme(axis.text.y = element_text(size=12))
ggsave(filename="M:/chart1.pdf", plot=p1)

##############################################################
## Chart 2: decr. in moves to sf/shared between periods 1-3 ##
##############################################################

xtabs.tosh <- read.csv("/users/shruthivenkatesh/documents/senior living/toSFshared.csv")
xtabs.tosh <- xtabs.tosh[(rowSums(is.na(xtabs.tosh)) == 0), ] 
xtabs.tosh <- xtabs.tosh[!(xtabs.tosh$agebucket %in% c("(85,90]", "(95,100]", "(90,95]")), ]
xtabs.tosh <- rename(xtabs.tosh, c("X1968.2011"="1968-2011", "X1968.1984"="1968-1984", "X1985.1995"="1985-1995", "X1996.2011"="1996-2011"))

m2 <- melt(xtabs.tosh, idvars=c("agebucket"), variable.name="time.period", value.name="toSL.share")
p2 <- ggplot(m2, aes(x=agebucket, y=value, col=variable, group=variable, line=20)) + geom_line(size=1.5)
p2 <- p2 + labs(x="Age group",
                y="Moves to shared or single family housing as share of total moves",
                title="Moves to Shared of Single Family Homes as a Fraction of Total Transitions") 
p2 <- p2 + scale_color_discrete("Time Period") + theme_bw(base_size = 14, base_family="Helvetica")
p2 <- p2 + theme(axis.text.y = element_text(size=12))
ggsave(filename="/users/shruthivenkatesh/documents/senior living/paper1/chart2.pdf", plot=p2)


################################################################
## Regression table: baseline and interaction frameworks, glm ##
################################################################
data <- read.csv(dird.55plus)
source(dir.logit)
# Keep only variables with information on education
data <- data[data$educ < 98, ]
data <- droplevels(data)
data$aip <- as.numeric(data$trans_from %in% c("Shared", "SF"))


fbase <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
  agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
  agebucket.100 + agebucket.105 +
  urban.rural.code.Urban + 
  race2.Black + race2.White +                         
  mar.Married +
  impwealth +
  educ +
  trans_from.SF + trans_from.Shared  

base.model <- glm(fbase, family=binomial(link="logit"), data=data)

fint <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
  agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
  agebucket.100 + agebucket.105 +
  urban.rural.code.Urban + 
  race2.Black + race2.White +
  mar.Married + 
  impwealth +
  educ +
  trans_from.SF : period1 + trans_from.Shared : period1 +
  trans_from.SF : period2 + trans_from.Shared : period2

int.model <- glm(fint, family=binomial(link="logit"), data=data)

fcombined <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
  agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
  agebucket.100 + agebucket.105 +
  urban.rural.code.Urban + 
  race2.Black + race2.White +
  mar.Married + 
  impwealth +
  educ +
  aip 

model.combined <- glm(fcombined, family=binomial(link="logit"), data=data)

fcombined.int <- trans_to.Senior ~ agebucket.60 + agebucket.65 + agebucket.70 + agebucket.75 +
  agebucket.80 + agebucket.85 + agebucket.90 + agebucket.95 + 
  agebucket.100 + agebucket.105 +
  urban.rural.code.Urban + 
  race2.Black + race2.White +
  mar.Married + 
  impwealth +
  educ +
  aip : period1 + aip : period2

model.combinedint <- glm(fcombined.int, family=binomial(link="logit"), data=data)



stargazer(base.model, int.model, 
          type = "latex", 
          omit = c("agebucket.60", "agebucket.65", "agebucket.70", "agebucket.75", "agebucket.80", "agebucket.85", "agebucket.90", "agebucket.95", "agebucket.100", "agebucket.105", "impwealth"),
          covariate.labels = c("Urban living status", "Race: black", "Race: white", "Married", "Education", "Transition from single family home", "Transition from a shared home", "Transition from single family home*period1", "Transition from shared home*period1", "Transition from single family home*period2", "Transition from shared home*period2"),
          dep.var.labels = c("Move to Senior Housing"),          
          notes = c("Standard errors in parentheses."),
          notes.append = TRUE,
          out.header = TRUE,
          title = c("Transitions to Senior Housing from Shared or Single Family Homes"),
          out = c("regtable1.tex")
          )

stargazer(model.combined, model.combinedint, 
          type = "latex", 
          out.header = TRUE,
          out = "regtable2.tex",
          omit = c("agebucket.60", "agebucket.65", "agebucket.70", "agebucket.75", "agebucket.80", "agebucket.85", "agebucket.90", "agebucket.95", "agebucket.100", "agebucket.105", "impwealth"),
          covariate.labels = c("Urban living status", "Race: black", "Race: white", "Married", "Education", "Transition from a shared or single family home", "Transition from shared or single family home*period1", "Transition from a shared or single family home*period2"),
          dep.var.labels = c("Move to Senior Housing"),
          title = c("Transition to Senior Housing from Aging in Place"),
          notes = c("Standard errors in parentheses."),
          notes.append = TRUE
          )



