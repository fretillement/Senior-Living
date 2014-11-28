require(dummies)
"
This program runs an example logit regression using the template provided
here: http://www.ats.ucla.edu/stat/r/dae/logit.htm
"

# Read and describe data
data = read.csv("http://www.ats.ucla.edu/stat/data/binary.csv")
colnames(data)
xtabs(~admit+gre+gpa+rank, data)
sapply(data, sd)
sapply(data, mean)

model1 = glm(admit ~ gre+gpa+rank, data=data, family="binomial")

# Convert the dep vars to factor, so glm knows to treat them as categorical
data$rank <- factor(data$rank)
model2 = glm(admit ~ gre+gpa+rank, data=data, family="binomial")

summary(model1)
summary(model2)
