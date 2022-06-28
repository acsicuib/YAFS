options(warn=-1)
args = commandArgs(trailingOnly=TRUE)
library(MCDA)

# ["Rscr]ipt",path+"/rscripts/test.R",arg1,arg2,"(1,2,3)","min,max,max"]
## TEMP
args[1]= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/exp_test/data"
args[2]= "/data11"
args[3] = 5 #numero criterios

args[4] = "1,2,3,2,2" #criteriaWeights

args[5] = "4,5,6,6,314,469,612,716,513,627,685,743,1778,4636,12471,16248,6,2,1,0"
args[6] = "min,min,min,min,max"
args[7] = "NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA"

majorityThreshold = 5

# node,hopcount,latency,power,deploymentPenalty,availabilityPenalty,utilization


#Adaptation parameters from args
pathIN <- paste(args[1],args[2],".csv",sep="")
pathOUT <- paste(args[1],args[2],"_r.csv",sep="")

print(pathIN)

# colClasses = c(NULL,rep("NA", count.fields(pathIN, sep=",")[1] -2 ))
# colClasses = c("NULL","numeric","numeric","numeric","numeric","numeric","numeric")
colClasses <- c("NULL",rep("numeric", count.fields(pathIN, sep=",")[1] -1))
dataOriginal <- read.table(file=pathIN, header=F, sep=",")
performanceTable <- read.table(file=pathIN, header=F, sep=",",colClasses=colClasses,skip=1)

nCriteria = as.integer(args[3])

criteriaWeights <- as.numeric(unlist(strsplit(args[4], ",")))

tmp <- as.numeric(unlist(strsplit(args[5], ",")))
categoriesLowerProfiles <- matrix(unlist(tmp), ncol = nCriteria, byrow = FALSE)

tmp <- as.numeric(unlist(strsplit(args[7], ",")))
criteriaVetos <- matrix(unlist(tmp), ncol = nCriteria, byrow = FALSE)

criteriaMinMax <- c(unlist(strsplit(args[6], ",")))



# categoriesLowerProfiles - 
# categoriesLowerProfiles <- rbind(c(1, 10),c(3, 20),c(NA,NA)) #per parameter
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


# MRSort
assignments<-MRSort(performanceTable, categoriesLowerProfiles,
                    categoriesRanks,criteriaWeights,
                    criteriaMinMax, majorityThreshold=majorityThreshold,
                    criteriaVetos = criteriaVetos)

# write.csv(assignments,pathOUT,quote = FALSE)
print(assignments)

# criteriaLBs=c(0,2,4,5)
# names(criteriaLBs) <- colnames(performanceTable)
# criteriaUBs=c(50,50,50,50)
# plotMRSortSortingProblem(performanceTable, categoriesLowerProfiles,
#                          categoriesRanks, assignments, criteriaMinMax,
#                          criteriaUBs, criteriaLBs)
