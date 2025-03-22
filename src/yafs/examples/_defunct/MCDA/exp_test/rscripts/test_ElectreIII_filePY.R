options(warn=-1)
library(OutrankingTools)
#dev.off()

args1= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args2= "/data"
pathIN <- paste(args1,args2,".csv",sep="")
colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
performanceTable <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)


#In this example we will use a linear threshold format. Thus we need to define two columns 
#of numeric values for each threshold, one for the slope (label beginning by alpha in the figure
#below) and another one for the interception (label beginning by beta) as shown below:
  
# Vector containing names of alternatives
alternatives <- rownames(performanceTable) 

# Vector containing names of criteria
criteria <- colnames(performanceTable)


# vector indicating the direction of the criteria evaluation .
minmaxcriteria <-c("min","min","min")

# criteriaWeights vector
#criteriaWeights <- c(0.3,0.1,0.3,0.2,0.1,0.2,0.1)
criteriaWeights <- c(0.33,0.33,0.33)

# thresholds vector
# alpha_q <- c(0.08,0.02,0,0,0.1,0,0)
# beta_q <- c(-2000,0,1,100,-0.5,0,3)
# 
# alpha_p <- c(0.13,0.05,0,0,0.2,0,0)
# beta_p <- c(-3000,0,2,200,-1,5,5)
# 
# alpha_v <- c(0.9,NA,0,NA,0.5,0,0)
# beta_v <- c(50000,NA,4,NA,3,15,15)

# Indifference
alpha_q <- c(0,0,0) 
beta_q <- c(0,0,0)

# Preference
alpha_p <- c(0.3,0.2,0.2) 
beta_p <- c(4,6,6)


#Veto
alpha_v <- c(NA,NA,0.3)
beta_v <- c(NA,NA,30)



# Vector containing the mode of definition which
# indicates the mode of calculation of the thresholds.
# mode_def <- c("I","D","D","D","D","D","D")
mode_def <- c("D","D","D")
# Testing
Electre3_AlphaBetaThresholds(performanceTable,
                             alternatives,
                             criteria,
                             minmaxcriteria,
                             criteriaWeights,
                             alpha_q,
                             beta_q,
                             alpha_p,
                             beta_p,
                             alpha_v,
                             beta_v,
                             mode_def)


args1= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args2= "/data"
pathIN <- paste(args1,args2,".csv",sep="")
colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -2))
performanceTable <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)



print("2 parte")
IndifferenceThresholds <- c(0,9)
PreferenceThresholds <- c(10,16)
VetoThresholds <- c(NA,NA)
criteriaWeights <- c(1,1)
criteria <- colnames(performanceTable)
minmaxcriteria <-c("min","max")
# Vector containing the mode of definition which
# indicates the mode of calculation of the thresholds.
# Testing
Electre3_SimpleThresholds(performanceTable,
                          alternatives,
                          criteria,
                          minmaxcriteria,
                          criteriaWeights,
                          IndifferenceThresholds,
                          PreferenceThresholds,
                          VetoThresholds)



performanceMatrix <- cbind(
  c(-14,129,-10,44,-14,-20),
  c(90,100,50,90,100,10),
  c(0,0,100,0,0,0),
  c(40,100,10,5,20,30),
  c(100,100,100,20,40,30)
)

args1= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args2= "/data"
pathIN <- paste(args1,args2,".csv",sep="")
colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
performanceMatrix <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)


performanceMatrix <- cbind(
  c(2,7,8,13,16),
  c(20,16,23,3,10)
)


alternatives <- c("Project1","Project2","Project3","Project4","Project5")
# Vector containing names of criteria
criteria <- c( "R","W")
# vector indicating the direction of the criteria evaluation
minmaxcriteria <- c("min","min")
# criteriaWeights vector
# thresholds vector
IndifferenceThresholds <- c(1,5)
PreferenceThresholds <- c(4,15)
VetoThresholds <- c(15,30)
criteriaWeights <- c(1,1)

out <- Electre3_SimpleThresholds(performanceMatrix,
                          alternatives,
                          criteria,
                          minmaxcriteria,
                          criteriaWeights,
                          IndifferenceThresholds,
                          PreferenceThresholds,
                          VetoThresholds)
# df <- data.frame(out['Final Ranking Matrix'])
# print(df["Final.Ranking.Matrix.alternative"])




#
# PARTE 4 probando con valores de la simulación
#



args3 =  "4,1,2,3,1"
args4 = "1.00000,99.93333,174.00000,820.00000,0.00000"
args5 =   "4.0,358.8,557.0,4220.0,20.0"
args6  =  "4.8,535.2,751.9200000000001,8324.0,22"
args6  =  "NA,NA,NA,NA,NA"
args7 = "min,min,min,min,max"

args1= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args2= "/data_0"

pathIN <- paste(args1,args2,".csv",sep="")
pathOUT <- paste(args1,args2,"_r.csv",sep="")

colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
performanceMatrix <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)

alternatives <- rownames(performanceMatrix)
criteria <- colnames(performanceMatrix)

criteriaWeights <- as.numeric(unlist(strsplit(args3, ",")))
IndifferenceThresholds <- as.numeric(unlist(strsplit(args4, ",")))
PreferenceThresholds <- as.numeric(unlist(strsplit(args5, ",")))
VetoThresholds <- as.numeric(unlist(strsplit(args6, ",")))
minmaxcriteria <- c(unlist(strsplit(args7, ",")))

out <- Electre3_SimpleThresholds(performanceMatrix,
                                 alternatives,
                                 criteria,
                                 minmaxcriteria,
                                 criteriaWeights,
                                 IndifferenceThresholds,
                                 PreferenceThresholds,
                                 VetoThresholds)
