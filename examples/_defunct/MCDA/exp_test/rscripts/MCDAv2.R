#!/usr/bin/env Rscript
library(MCDA)
options(warn=-1)
args = commandArgs(trailingOnly=TRUE)

## T
#args[1]= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/data"
#args[2]= "/data2"
#args[3] = 2 #numero criterios
#args[4] = "2,1" #criteriaWeights
#args[5] = "1,10,3,20,NA,NA" #categoriesLowerProfiles
#args[6] = "min,max" #criteriaMinMax
#args[7] = "NA,NA,NA,NA,NA,NA" #vetos
#args[8] = majorityThreshold

#Adaptation parameters from args
pathIN <- paste(args[1],args[2],".csv",sep="")
pathOUT <- paste(args[1],args[2],"_r.csv",sep="")

print(pathIN)
# colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
# performanceTable <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)
performanceTable <- read.table(file=pathIN, header=F, sep=",")
print(performanceTable)

nCriteria = as.integer(args[3])
majorityThreshold = as.integer(args[8])

criteriaWeights <- as.numeric(unlist(strsplit(args[4], ",")))

tmp <- as.numeric(unlist(strsplit(args[5], ",")))
categoriesLowerProfiles <- matrix(unlist(tmp), ncol = nCriteria, byrow = FALSE)
print(categoriesLowerProfiles)

tmp <- as.numeric(unlist(strsplit(args[7], ",")))
criteriaVetos <- matrix(unlist(tmp), ncol = nCriteria, byrow = FALSE)

criteriaMinMax <- c(unlist(strsplit(args[6], ",")))

print(criteriaMinMax)

# categoriesLowerProfiles - 
# categoriesLowerProfiles <- rbind(c(1, 10),c(3, 20),c(NA,NA)) #per parameter
print(colnames(performanceTable))
colnames(categoriesLowerProfiles) <- colnames(performanceTable)
rownames(categoriesLowerProfiles)<-c("A","B","C","D")


# No tocar
# the order of the categories, 1 being the best
categoriesRanks <-c(1,2,3,4)
names(categoriesRanks) <- c("A","B","C","D")

#
# criteria to minimize or maximize
# criteriaMinMax <- c("min","max") #per parameter
names(criteriaMinMax) <- colnames(performanceTable)

# vetos
# A partir de dicho valor, ya no puede ser de dicho criterio
# criteriaVetos <- rbind(c(NA,NA),c(4, 7),c(6,NA))
colnames(criteriaVetos) <- colnames(performanceTable)
rownames(criteriaVetos) <- c("A","B","C","D")


# weights
# criteriaWeights <- c(1,2) #per parameter
names(criteriaWeights) <- colnames(performanceTable)

print(criteriaWeights)
# MRSort
assignments<-MRSort(performanceTable, categoriesLowerProfiles,
                    categoriesRanks,criteriaWeights,
                    criteriaMinMax, majorityThreshold=majorityThreshold,
                    criteriaVetos = criteriaVetos)

write.csv(assignments,pathOUT,quote = FALSE)
print(assignments)
