from subprocess import Popen, PIPE
import os
import logging
import time
import numpy as np
import operator

np.random.seed(1)

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S', level=logging.DEBUG)

def sort_table(table, col=0):
    return sorted(table, key=operator.itemgetter(col))

#see https://docs.python.org/3/library/subprocess.html#module-subprocess
def runMCDAR(pathRScript,pathWD,fileName,ncriteria,criteriaWeights,categoriesLowerProfiles,
             criteriaMinMax,criteriaVetos,majorityThreshold):
    cmd = ["Rscript",pathRScript+"/rscripts/MCDAv2.R",pathWD,fileName,ncriteria,criteriaWeights,categoriesLowerProfiles,
             criteriaMinMax,criteriaVetos,majorityThreshold]
    proc = Popen(cmd, stdout=PIPE)
    stdout = proc.communicate()[0]
    print stdout



    return  '{}'.format(stdout)
        
#Init 
#print os.getcwd()
pathTMP = "tmp/"
path = os.getcwd()+"/exp_test/"    

# Creating data
nprojects = 7
ncriteria = 5
nrankcategories = 4
majorityThreshold = ncriteria

#categoriesRanks = ["A","B","C"] #The same categories in R-scripts: A > B > C

logging.info("Creating FAKE data")

data = np.random.randint(1,20,size=(nprojects,ncriteria)) # values matrix
#print data
data = np.array([[2032,5,20,20,0], [1231,0,40,20,1], [3323,6,20,0,5],[13323,6,20,0,5],
                 [2432,5,20,20,0],[9032,5,20,20,0],[122032,5,20,20,0],
                 [4323,6,20,0,5]])
#data = np.array([[5,20,20], [0,40,20], [6,20,0]])
#data = np.array([[5], [0], [6]])
nprojects = len(data)
print "DATA"
print data

np.percentile(data[:,0],10)


lp = [str(int(np.percentile(data[:,0],p))) for p in [1, 40, 60, 80]]
lp2 = [str(int(np.percentile(data[:,1],p))) for p in range(20,100,20)]
lp3 = [str(int(np.percentile(data[:,2],p))) for p in range(20,100,20)]
lp4 = [str(int(np.percentile(data[:,3],p))) for p in range(20,100,20)]
lp5 = [str(int(np.percentile(data[:,4],p))) for p in range(20,100,20)]
clp = np.vstack((lp,lp2,lp3,lp4,lp5))





#clp = np.vstack((lp))
categoriesLowerProfiles = ",".join(str(x) for x in clp.flatten())

print "--"*20
print "Categories Lower Profile"
print "--"*20
print categoriesLowerProfiles        
print "--"*20
print ""

criteriaWeights = ",".join(str(x) for x in range(1,ncriteria+1))         #r-argument
criteriaWeights ="4,2,3,3,1"
#criteriaWeights ="1,1,1,1,1" # con MCDA - TODOS SACAN LA PEOR NOTA



#criteriaWeights ="1"

criteriaMinMax =  ",".join(str(x) for x in np.random.choice(["min","max"],ncriteria))
criteriaMinMax  = "min,min,min,min,max"
#criteriaMinMax  = "min"

vetos = ("NA,"*ncriteria*nrankcategories)[:-1]
#vetos = "NA,NA,NA,NA"


#Creating control directory
datestamp = time.strftime('%Y%m%d%H%M%S')
datestamp = "20181109123421"
dname = path+pathTMP+datestamp+"/"
#os.makedirs(dname)
logging.info("Creating directory: "+ dname)

#Storing data in directory
np.savetxt(dname+"data.csv",data, delimiter=",",fmt='%i')

#Run process 
logging.info("Running R-script")


output= runMCDAR(pathRScript=path,pathWD=dname,fileName="data",ncriteria=str(ncriteria),
                 criteriaWeights=criteriaWeights,categoriesLowerProfiles=categoriesLowerProfiles,
                 criteriaMinMax=criteriaMinMax,criteriaVetos=vetos,majorityThreshold=str(majorityThreshold))

#Transform output
#logging.info("Transforming data")
#print output
#output = output.replace("\"","")
#weights = output.split()[nprojects:]
#table = zip(range(nprojects),weights)
#table = sort_table(table, 1)
#
##Best project
#choice = table[0][0]
#print choice
##        


# Normalizacion de la matri
data[:,4] = np.abs(data[:,4] - data[:,4].max())

criteriaWeights= np.array([int(x) for x in criteriaWeights.split(",")])
col_sums = data.sum(axis=0)
new_matrix = np.true_divide(data,col_sums)

choice = []
for r in range(len(data)):
    choice.append(np.average(new_matrix[r], weights=criteriaWeights))
    
print choice 
print "Best choice: "
print np.array(choice).argsort()

    





