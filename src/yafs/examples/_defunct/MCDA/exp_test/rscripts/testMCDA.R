#!/usr/bin/env Rscript
library(MCDA)
# setwd("/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/rscripts/")


args = commandArgs(trailingOnly=TRUE)
pathIN <- paste(args[1],args[2],".csv",sep="")
pathOUT <- paste(args[1],args[2],"_r.csv",sep="")

# https://cran.r-project.org/web/packages/MCDA/MCDA.pdf
# the performance table

MyData <- read.table(file=pathIN, header=F, sep=",")
rownames(MyData) <- c(1:nrow(MyData))
colnames(MyData) <- c("Price","Time","Comfort")


performanceTable <- MyData

# performanceTable <- rbind(
#   c(1,10,1),
#   c(4,20,2),
#   c(2,20,0),
#   c(6,40,0),
#   c(30,30,3))
# 
# rownames(performanceTable) <- c("RER","METRO1","METRO2","BUS","TAXI")
# colnames(performanceTable) <- c("Price","Time","Comfort")


# lower profiles of the categories
# (best category in the first position of the list)
categoriesLowerProfiles <- rbind(c(3, 11, 3),c(7, 25, 2),c(NA,NA,NA))

colnames(categoriesLowerProfiles) <- colnames(performanceTable)
rownames(categoriesLowerProfiles)<-c("A","B","C")
# the order of the categories, 1 being the best
categoriesRanks <-c(1,2,3)
names(categoriesRanks) <- c("A","B","C")
# criteria to minimize or maximize
criteriaMinMax <- c("min","min","max")
names(criteriaMinMax) <- colnames(performanceTable)
# vetos
criteriaVetos <- rbind(c(10, NA, NA),c(NA, NA, 1),c(NA,NA,NA))
colnames(criteriaVetos) <- colnames(performanceTable)
rownames(criteriaVetos) <- c("A","B","C")
# weightsa
criteriaWeights <- c(1,3,2)
names(criteriaWeights) <- colnames(performanceTable)

# MRSort
assignments<-MRSort(performanceTable, categoriesLowerProfiles,
                    categoriesRanks,criteriaWeights,
                    criteriaMinMax, 3,
                    criteriaVetos = criteriaVetos)

write.csv(assignments,pathOUT,quote = FALSE)
print(assignments)
