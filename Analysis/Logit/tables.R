require(stargazer)
require(plyr)
require(matrixStats)
require(ggplot2)
require(reshape2)
require(ggsave)
require(ggsave.latex)

# This script generates the tables and charts in latex on elderly 
# housing choice measured by the PSID. 
#
# For more information about the data, see get_complete.py
#
# Dependencies: crosstabs.R, logit.R
#

# Set directories
dird.55plus <- "M:/senior living/data/Psid data/complete_st-logit.csv"
dird.complete <- "M:/senior living/data/psid data/complete_st.csv"
dirh <-  "M:/senior living/code/senior-living/analysis/logit/housekeeping.R"
dir.xtabs <- "M:/senior living/code/senior-living/analysis/Crosstabs/xtabs.R"
dir.xtabsdata <- "M:/senior living/data/psid data/tosr_share.csv"
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




