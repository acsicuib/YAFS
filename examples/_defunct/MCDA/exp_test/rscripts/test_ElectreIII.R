options(warn=-1)
library(OutrankingTools)

## Illustrative example used to present the ELECTRE III-IV software in the French version.
## The objective: make the ranking of 10 French cars that were evaluated on 7 criteria
##(VALLE E, D. AND ZIELNIEWICZ, P. (1994a).
## Document du LAMSADE 85, Universite Paris-Dauphine,Paris.)
## the performance table
performanceMatrix <- cbind(
  c(103000,101300,156400,267400,49900,103600,103000,170100,279700,405000),
  c(171.3,205.3,221.7,230.7,122.6,205.1,178.0,226.0,233.8,265.0),
  c(7.65,7.90,7.90,10.50,8.30,8.20,7.20,9.10,10.90,10.30),
  c(352,203,391,419,120,265,419,419,359,265),
  c(11.6,8.4,8.4,8.6,23.7,8.1,11.4,8.1,7.8,6.0),
  c(88.0,78.3,81.5,64.7,74.1,81.7,77.6,74.7,75.5,74.7),
  c(69.7,73.4,69.0,65.6,76.4,73.6,66.2,71.7,70.9,72.0))

args[1]= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args[2]= "/data0"
pathIN <- paste(args[1],args[2],".csv",sep="")
colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
performanceTable <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)


# Vector containing names of alternatives
alternatives<-c("CBX16","P205G","P405M","P605S","R4GTL","RCLIO","R21TS","R21TU","R25BA","ALPIN")

rownames(performanceMatrix) <- alternatives
# Vector containing names of criteria
criteria <-c("Prix","Vmax","C120","Coff","Acce","Frei","Brui")

colnames(performanceMatrix ) <- criteria
# vector indicating the direction of the criteria evaluation .
minmaxcriteria <-c("min","max","min","max","min","min","min")
# criteriaWeights vector
criteriaWeights <- c(0.3,0.1,0.3,0.2,0.1,0.2,0.1)
# thresholds vector
alpha_q <- c(0.08,0.02,0,0,0.1,0,0)

beta_q <- c(-2000,0,1,100,-0.5,0,3)
alpha_p <- c(0.13,0.05,0,0,0.2,0,0)
beta_p <- c(-3000,0,2,200,-1,5,5)
alpha_v <- c(0.9,NA,0,NA,0.5,0,0)
beta_v <- c(50000,NA,4,NA,3,15,15)
# Vector containing the mode of definition which
# indicates the mode of calculation of the thresholds.
mode_def <- c("I","D","D","D","D","D","D")
# Testing
Electre3_AlphaBetaThresholds(performanceMatrix,
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
