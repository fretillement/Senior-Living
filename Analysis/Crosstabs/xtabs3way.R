require(plyr)

# This script generates a 3D table of occupancy type by wealth
# decile and age group for those 55 and older in years 1984- in the PSID. 
#
# See get_complete.py for more info on the raw PSID data
# 


# Read in the data & clean up 
clean.dir <- "M:/senior living/code/senior-living/analysis/housekeeping.R"
source(clean.dir)

# Keep only wealth years; Generate a wealth decile variable FOR EVERY YEAR 
wmeasured <- c(1984, 1989, seq(1999, 2011, 2))
data <- data[(data$year %in% wmeasured), ]
getdecile <- function(yeardf) { 
    yeardf$wealthd <- cut(yeardf$impwealth, quantile(yeardf$impwealth, seq(0, 1, .1), na.rm = TRUE), include.lowest = TRUE)
    yeardf$wealthd <- as.numeric(factor(yeardf$wealthd))
    return(yeardf)
    }
data <- ddply(getdecile, .variables = 'year', .data = data, .parallel = TRUE)


# Get obs count by age bucket (col) and housing occupancy (col) by wealth decile (row)

 