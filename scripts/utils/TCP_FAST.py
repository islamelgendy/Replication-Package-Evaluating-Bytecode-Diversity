from utils.Hybrid_selection import HybridSelection
from utils.utilsSystem import createFolder
from utils.Coverage_selection import CoverageSelection

from utils.Diversity_selection import DiversitySelection
from utils.CSVLoader import CSVLoader, evaluateMutationScore
from utils.Hybrid_selection_combined import CombinedHybridSelection
from utils.Hybrid_selection_separate import SeparateHybridSelection
import sys

from utils.testsCoveringMutants import getCategorizedMutants, getMutants, getTestsExecutingMutants, normalizeTests
from utils.utilsIO import *
import pickle

# Load the saved pickle file
def loadPickleFile(file):
    with open(file, "rb") as f:
        loaded_prioritization = pickle.load(f)

    return loaded_prioritization

# Load the saved method names
def loadMethodNames(file):
    methodDict = dict()
    with open(file, "r") as f:
        contents = f.readlines()
    
    for i in range(len(contents)):
        methodDict[i+1] = contents[i][:-1]

    return methodDict

def updateFaultDetection(methodName, fault_tests, probability, FDList, raceIndex, key, realfaultRace):

    if FDList[-1] != 1 and methodName in fault_tests:
        realfaultRace[key] = raceIndex + 1

    if FDList[-1] == 1 or methodName in fault_tests:
            if not key in realfaultRace.keys():
                realfaultRace[key] = raceIndex + 1
            FDList.append(1)
    else:
        FDList.append(probability)

def checkRaceDictionary(race, maxSize):
    if not 'FASTpw' in race.keys():
        race['FASTpw'] = maxSize

def runExp(root, project, id, testType, aftercoverage = True, isBranchCoverage = False):

    if testType == 'Randoop':
        FASTfile = '/home/islam/MyWork/Code/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1-Randoop.pickle'.format(project, id)
        methodNamesFile = f'/home/islam/MyWork/Code/FAST-replication/input/{project}_v{id}/{project}-keys-Randoop.txt'
    elif testType == 'Evosuite':
        FASTfile = '/home/islam/MyWork/Code/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1-Evosuite.pickle'.format(project, id)
        methodNamesFile = f'/home/islam/MyWork/Code/FAST-replication/input/{project}_v{id}/{project}-keys-Evosuite.txt'
    elif testType == 'Developer':
        FASTfile = '/home/islam/MyWork/Code/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1-Developer.pickle'.format(project, id)
        methodNamesFile = f'/home/islam/MyWork/Code/FAST-replication/input/{project}_v{id}/{project}-keys-Developer.txt'
    elif testType == 'bytecode':
        FASTfile = '/home/islam/MyWork/Code/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1-bytecode.pickle'.format(project, id)
        methodNamesFile = f'/home/islam/MyWork/Code/FAST-replication/input/{project}_v{id}/{project}-keys-bytecode.txt'
    
    else:    
        FASTfile = '/home/islam/MyWork/Code/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1.pickle'.format(project, id)
        methodNamesFile = f'/home/islam/MyWork/Code/FAST-replication/input/{project}_v{id}/{project}-keys.txt'
    mutationFolder = root + "/resources/mutation/"
    realfaultFolder = root + "/resources/realfault/"
    mutationExt = 'mutation.csv'
    realfaultExt = "realfaults-detected.csv"
    fault_tests = list()

   
    # Load the FAST priotization
    FASTlist = loadPickleFile(FASTfile)

    # Load the keys (method names)
    methodNames = loadMethodNames(methodNamesFile)

    # Load the mutation file into CSVLoader obj
    try:
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
        mutationCSV = CSVLoader(mutationFile)
    except:
        print('Mutation file can NOT be loaded')
    
    # Load the real-faults files into fault_tests list
    try:
        realfaultFile = filterFiles(realfaultFolder, project + '.' + id + 'f', realfaultExt)[0]
        fault_tests = processRealFaultFile(realfaultFile)

    except:
        print('Real-fault files can NOT be loaded')


    # with open(statementCoverageFile, "r") as f:
    #     covContents = f.readlines()
        
    # killingTests, lineNumbers = getMutants(mutContents)

    # coveringTests = getTestsExecutingMutants(covContents, lineNumbers)

    # normalizedSetOfTests = normalizeTests(coveringTests)

    # # calculate the original statement coverage
    # totalStatementCoverage = statementCSV.getTotalCoverage()

    # calculate the original mutation score 
    MS = mutationCSV.getTotalCoverage()

    # print('statement coverage ', totalStatementCoverage)
    # print('mutation score ', MS)

    MS4 = list()
    diversitySize =  len(FASTlist) 
    
    # selectionPoolSize = len(randomObj.selectionPool)
      
    # race list: who reaches the max MS first
    realfaultRace = dict()

    # race list: who reaches the max MS first
    race = dict()

    raceIndex = 0
    FASTFlag = False
    
    totalNumTests = len(FASTlist)            # Total number of tests
    numberFaultTests = len(fault_tests)                         # Number of fault-detecting tests
    FDprobability = numberFaultTests / totalNumTests            # Initial probability of fault detection

    FD4 = [FDprobability]

    # Walk through the FASTlist one element at a time
    Plist = []
    
    # while combinedhybridObject.coverage < totalStatementCoverage or coverageObj.coverage < totalStatementCoverage:
    for i in range(diversitySize):
        Plist.append( methodNames[ FASTlist[i] ] )
        
        # print(diversityObject.matrixP.keys())
        score4 = evaluateMutationScore(mutationCSV.matrix, Plist, mutationCSV.listCols)
        
        if score4 == MS and not FASTFlag:
            FASTFlag = True
            race['FASTpw'] = raceIndex
        
        MS4.append(score4)
        
        # Check the fault detection probabilibity 
        remaining_tests = totalNumTests - (raceIndex + 1)
        probability = numberFaultTests / remaining_tests if remaining_tests > 0 else 0

        updateFaultDetection(Plist[i], fault_tests, probability, FD4, raceIndex, 'FASTpw', realfaultRace)
        
        raceIndex += 1
    # obj.makeOneSelection()

    # Calculate the APFDs
    APFD = list()
    APFD4 = calculateAPFD(Plist, mutationCSV)
    
    if len(realfaultRace) == 0:
        checkRaceDictionary(realfaultRace, diversitySize)
    
    # DONE: Report the APFDs back to plot them in box plots
    return APFD4, realfaultRace

# Calcuate the APFD given the permutation of tests and the mutants
def calculateAPFD(matrixP, mutationCSV):

    mutantList = evaluateMutants(mutationCSV.matrix, mutationCSV.listCols, matrixP)

    n = len(matrixP) # the number of tests
    m = len(mutantList) # the number of killable mutants 

    if m == 0:
        return 0

    # Get the sum of the indecies
    sum = 0
    for mutant in mutantList.keys():
        sum += mutantList[mutant]

    # The equation to calculate APFD
    APFD = 1 - (sum / (n*m)) + (1 / (2*n))

    return APFD

# Return a list of killed mutants and the index of the test that killed it from the passed permutation
def evaluateMutants(mutMatrix, mutantList, evalMethods):
    # list of mutants
    covered = dict()

    # For each mutant, check the permutation one by one
    for mutant in mutantList:
        index = 1
        covered[mutant] = 0
        for curMethod in evalMethods:
            if curMethod in mutMatrix:
                curRecord = mutMatrix[curMethod]
                value = curRecord[mutant]
                if value == '1':
                    covered[mutant] = index
                    break
            index += 1
        
        # If the mutant is still 0, then no test is killing it and remove it
        if covered[mutant] == 0:
            covered.pop(mutant)
        
    return covered

# runExp('math', '23', 'randoop')



args = sys.argv
lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]

if len(args) == 1:
    prj = "compress"
    testType = 'bytecode'
    coverageType = 'Branch'
elif len(args) == 2:
    prj = args[1]
    testType = 'bytecode'
    coverageType = 'Branch'
elif len(args) == 3:
    prj = args[1]
    testType = args[2]
    coverageType = 'Branch'
else: 
    print('Wrong number of arugments passed')
    exit()

# math projects:
# prj = 'math'
if prj == 'math':
    projects = ['4', '5', '6', '9', '13', '14', '18', '17', '19',
                '20', '21', '23', '24', '25', '26', '27', '28', 
                '30', '32', '33', '37', '42', '47', '49', '50', 
                '51', '52', '54', '56', '58', '61', '64', '65', 
                '67', '68', '69', '70', '73', '78', '76', '80', '81']
    # projects = ['4', '5', '6', '9', '13', '14', '18', '17', '19',
    #             '20', '21', '23', '24', '25', '26', '27', '28', 
    #             '30', '32', '33', '37', '42', '47', '49', '50', 
    #             '51', '52', '54', '56', '58', '64', '65', 
    #             '67', '68', '69', '70', '73', '78', '76', '80', '81']   # Developer

# jsoup projects:
# prj = 'jsoup'
elif prj == 'jsoup':
    projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                '30', '33', '35', '36', '37', '38', '39', '40']

# lang projects:
# prj = 'lang'
elif prj == 'lang':
    projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
    # projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33']  #Evosuite

# time projects:
# prj = 'time'
elif prj == 'time':
    projects = ['11','13']

# cli projects:
# prj = 'cli'
elif prj == 'cli':
    projects = ['30','31','32','33','34']
    # projects = ['31','34']

# csv projects:
# prj = 'csv'
elif prj == 'csv':
    projects = ['2', '3', '4', '5', '7', '8', '10', '11', '12', '16']
    # projects = ['2', '3', '4',           '8',             '12']

# Codec jacoco coverage is not generating, so it is not working
# codec projects:
# prj = 'codec'
# projects = ['11', '12', '15', '16']

# compress projects:
# prj = 'compress'
elif prj == 'compress':
    projects = ['1', '11', '16', '22', '24', '26', '27']
    # projects = ['1', '11', '16', '22', '24', '27']    #Evosuite
    # projects = ['11', '16', '22', '24', '26', '27']    #Developer

FASTAPFD = []
FASTFDRace = []


for id in projects:
    # try:
        print('Running Project ' + str(id) + '...')
        # runExp('math', id, '')
        da4, realFaultRace = runExp(root, prj, id, testType, False, coverageType == 'Branch')
        print(f'APFD is: {da4}')
        # da1, da2, da3, da4, da5 = runExp(root, prj, id, 'dev')
        # ra1, ra2, ra3, ra4, ra5 = runExp(root, prj, id, 'randoop')

        # Add the APFD values into their list to produce the box plots
        if da4 < 1:
            FASTAPFD.append( round(da4*100, 2) )
        
        # Save the real fault indecies
        FASTFDRace.append( realFaultRace['FASTpw'])
        
    # except:
    #     print('Project ' + str(id) + ' failed to run properly')

msplotFile = root + '/PlotGeneration/after-coverage/' + prj + '/' + prj + '-APFD.py'
realfaultplotFile = root + '/PlotGeneration/after-coverage/' + prj + '/' + prj + '-realfault.py'
dstPlot = root + '/resources/plots/' + prj
createFolder(root + '/resources/plots/')
print('APFD = ', FASTAPFD)

print('Realfault race = ', FASTFDRace)
