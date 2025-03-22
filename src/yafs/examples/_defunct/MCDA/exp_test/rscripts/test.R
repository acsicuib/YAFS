args = commandArgs(trailingOnly=TRUE)

# ["Rscr]ipt",path+"/rscripts/test.R",arg1,arg2,"(1,2,3)","min,max,max"]
args[1]= "/Users/isaaclera/PycharmProjects/YAFS/src/examples/MCDA/data"
args[2]= "/data"

args[3] = "(1,2,3)"
args[4] = "min,max,max"

pathIN <- paste(args[1],args[2],".csv",sep="")
pathOUT <- paste(args[1],args[2],"_r.csv",sep="")

print(pathIN)

performanceTable <- read.table(file=pathIN, header=F, sep=",")

# categoriesLowerProfiles - 
categoriesLowerProfiles <- rbind(c(3, 11, 3),c(7, 25, 2),c(NA,NA,NA))
colnames(categoriesLowerProfiles) <- colnames(performanceTable)
rownames(categoriesLowerProfiles)<-c("A","B","C")

#
# the order of the categories, 1 being the best
categoriesRanks <-c(1,2,3)
names(categoriesRanks) <- c("A","B","C")

#
# criteria to minimize or maximize
criteriaMinMax <- c("min","min","max")
names(criteriaMinMax) <- colnames(performanceTable)

# vetos
criteriaVetos <- rbind(c(10, NA, NA),c(NA, NA, 1),c(NA,NA,NA))
colnames(criteriaVetos) <- colnames(performanceTable)
rownames(criteriaVetos) <- c("A","B","C")


# weightsa
#criteriaWeights <- c(1,3,2)
names(criteriaWeights) <- colnames(performanceTable)

print(performanceTable)

# MRSort
assignments<-MRSort(performanceTable, categoriesLowerProfiles,
                    categoriesRanks,criteriaWeights,
                    criteriaMinMax, 3,
                    criteriaVetos = criteriaVetos)

# write.csv(assignments,pathOUT,quote = FALSE)
print(assignments)

criteriaMinMax <- c(as.list(strsplit(args[4], ",")))
print(criteriaMinMax)

plotMRSortSortingProblem(performanceTable, categoriesLowerProfiles, 
                         categoriesRanks, assignments, criteriaMinMax, 
                         criteriaUBs, criteriaLBs)
