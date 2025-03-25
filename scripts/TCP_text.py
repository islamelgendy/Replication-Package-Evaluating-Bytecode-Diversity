import time

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
    if not 'diversity' in race.keys():
        race['diversity'] = maxSize

def runExp(root, project, id, testType, aftercoverage = True, isBranchCoverage = False):

    coverageFolder = root + "/resources/coverage/"
    mutationFolder = root + "/resources/mutation/"
    similarityFolder = root + "/resources/similarity/"
    realfaultFolder = root + "/resources/realfault/"
    if isBranchCoverage:
        coverageExt = 'branch.coverage.csv'
    else:
        coverageExt = 'statement.coverage.csv'
    similarityExt = 'textSimilarity.csv'
    bytecodeExt = 'byteCodeSimilarity.bytes.csv'
    mutationExt = 'mutation.csv'
    realfaultExt = "realfaults-detected.csv"
    fault_tests = list()

   
    # Load the coverage files into CSVLoader obj
    try:
        statementCoverageFile = filterFiles(coverageFolder, project + '.' + id + 'f', coverageExt)[0]
        statementCSV = CSVLoader(statementCoverageFile) 
    except:
        print('Statement coverage files can NOT be loaded')

    # Load the mutation file into CSVLoader obj
    try:
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
        mutationCSV = CSVLoader(mutationFile)
    except:
        print('Mutation file can NOT be loaded')

    # Load the textual similarity matrix
    try:
        if testType == 'Randoop':
            similarityFile = filterFiles(similarityFolder + project + '/auto/randoop', project + '.' + id + 'f', 'textSimilarity.randoop.csv')[0]
        else:    
            similarityFile = filterFiles(similarityFolder, project + '.' + id + 'f', similarityExt)[0]
        simlarityCSV = CSVLoader(similarityFile)
    except:
        print('Similarity matrix can NOT be loaded')
    
    # Load the real-faults files into fault_tests list
    try:
        realfaultFile = filterFiles(realfaultFolder, project + '.' + id + 'f', realfaultExt)[0]
        fault_tests = processRealFaultFile(realfaultFile)

    except:
        print('Real-fault files can NOT be loaded')

    with open(mutationFile, "r") as f:
        mutContents = f.readlines()

    with open(statementCoverageFile, "r") as f:
        covContents = f.readlines()
        
    killingTests, lineNumbers = getMutants(mutContents)

    coveringTests = getTestsExecutingMutants(covContents, lineNumbers)

    normalizedSetOfTests = normalizeTests(coveringTests)

    # calculate the original statement coverage
    totalStatementCoverage = statementCSV.getTotalCoverage()

    # calculate the original mutation score 
    MS = mutationCSV.getTotalCoverage()

    print('statement coverage ', totalStatementCoverage)
    print('mutation score ', MS)

    MS4 = list()
    # MS7 = list()

    if aftercoverage:
        coverageObj = CoverageSelection(statementCSV, branch=isBranchCoverage)
        coverageSize =  len(coverageObj.matrix)

        # Build a matrix that has the same coverage of the original
        foundationMS = list()
        foundationMethods = list()
        
        while coverageObj.coverage < totalStatementCoverage:
            mtd = coverageObj.makeOneSelectionAdditionalCoverage()
            score = evaluateMutationScore(mutationCSV.matrix, coverageObj.matrixP.keys(), mutationCSV.listCols)
            foundationMS.append(score)
            foundationMethods.append(mtd)
            MS4.append(score)
            
            # MS7.append(score)
        
        foundation = coverageObj.matrixP.keys()
    else:
        foundation = None
    # We already have the current mutation score achieved in the foundationMS list

    # Now, we have the smallest possible list that is achieving the same coverage as the original
    # The list should kill all the easy mutants as we simply executed the highest coverage
    # Next, we use that list as the foundation to continue the selection process until in various ways 
    # until the end of the test suite to kill the harder mutants
    
    # randomCoverageList = list()
    
    # Get the easy, stubborn, and unreachable mutants
    # easyMutants, stubbornMutants, unreachableMutants = getCategorizedMutants(foundationMethods, killingTests)

    # randomObj = CoverageSelection(statementCSV, foundation, branch=isBranchCoverage)#, normalizedSetOfTests)   
    diversityTextObject = DiversitySelection(simlarityCSV, foundation)
    # separatehybridObject = SeparateHybridSelection(statementCSV, simlarityCSV, coverageObj.matrixP.keys())# normalizedSetOfTests)

    diversitySize =  len(diversityTextObject.matrix) + len(diversityTextObject.matrixP)
    
    # selectionPoolSize = len(randomObj.selectionPool)
      
    # race list: who reaches the max MS first
    realfaultRace = dict()

    # race list: who reaches the max MS first
    race = dict()
    if aftercoverage:
        raceIndex = len(foundation)
        minSize = min(coverageSize, diversitySize)
    else:
        raceIndex = 0
        minSize = diversitySize
    bytecodeFlag = False
    
    totalNumTests = len(diversityTextObject.matrix.keys())            # Total number of tests
    numberFaultTests = len(fault_tests)                         # Number of fault-detecting tests
    FDprobability = numberFaultTests / totalNumTests            # Initial probability of fault detection

    FD4 = [FDprobability]
    
    # while combinedhybridObject.coverage < totalStatementCoverage or coverageObj.coverage < totalStatementCoverage:
    totalTime = 0
    iteration, total = 0, minSize
    while len(diversityTextObject.matrixP) < minSize:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()
        mh_t = time.process_time()
        textMethod = diversityTextObject.makeOneSelection()
        mh_time = time.process_time() - mh_t
        totalTime += mh_time
        # print(diversityObject.matrixP.keys())
        score4 = evaluateMutationScore(mutationCSV.matrix, diversityTextObject.matrixP.keys(), mutationCSV.listCols)
        
        if score4 == MS and not bytecodeFlag:
            bytecodeFlag = True
            race['diversity'] = raceIndex
        
        MS4.append(score4)
        
        # Check the fault detection probabilibity 
        remaining_tests = totalNumTests - (raceIndex + 1)
        probability = numberFaultTests / remaining_tests if remaining_tests > 0 else 0

        updateFaultDetection(textMethod, fault_tests, probability, FD4, raceIndex, 'diversity', realfaultRace)
        
        raceIndex += 1
    # obj.makeOneSelection()

    
    # Calculate the APFDs
    APFD = list()
    APFD4 = calculateAPFD(diversityTextObject.matrixP, mutationCSV)

    print(f"Time is {totalTime} sec.")
    
    if len(realfaultRace) == 0:
        checkRaceDictionary(realfaultRace, len(diversityTextObject.matrixP))
    
    # DONE: Report the APFDs back to plot them in box plots
    return APFD4, realfaultRace, totalTime

# Calcuate the APFD given the permutation of tests and the mutants
def calculateAPFD(matrixP, mutationCSV):

    mutantList = evaluateMutants(mutationCSV.matrix, mutationCSV.listCols, matrixP.keys())

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
    prj = "time"
    coverageType = 'Branch'
elif len(args) == 2:
    prj = args[1]
    coverageType = 'Branch'
elif len(args) == 3:
    prj = args[1]
    coverageType = args[2]
else: 
    print('Wrong number of arugments passed')
    exit()

# math projects:
# prj = 'math'
if prj == 'math':
    projects = ['4', '5', '6', '9', '13', '14', '17', '18', '19',
                '20', '21', '23', '24', '25', '26', '27', '28', 
                '30', '32', '33', '37', '42', '47', '49', '50', 
                '51', '52', '54', '56', '58', '61', '64', '65', 
                '67', '68', '69', '70', '73', '76', '78', '80', '81']

# jsoup projects:
# prj = 'jsoup'
elif prj == 'jsoup':
    projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                '30', '33', '35', '36', '37', '38', '39', '40']

# lang projects:
# prj = 'lang'
elif prj == 'lang':
    projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
    

# time projects:
# prj = 'time'
elif prj == 'time':
    projects = ['11','13']

# cli projects:
# prj = 'cli'
elif prj == 'cli':
    projects = ['30','31','32','33','34']
    

# csv projects:
# prj = 'csv'
elif prj == 'csv':
    projects = ['2', '3', '4', '5', '7', '8', '10', '11', '12', '16']
    

# Codec jacoco coverage is not generating, so it is not working
# codec projects:
# prj = 'codec'
# projects = ['11', '12', '15', '16']

# compress projects:
# prj = 'compress'
elif prj == 'compress':
    projects = ['1', '11', '16', '22', '24', '26', '27']
    # projects = ['24']

bytecodeAPFD = []
bytecodeFDRace = []
times = []


for id in projects:
    # try:
        print('Running Project ' + str(id) + '...')
        # runExp('math', id, '')
        da4, realFaultRace, mhtime = runExp(root, prj, id, 'Randoop', False, coverageType == 'Branch')
        print(f'APFD is: {da4}')
        times.append(mhtime)
        # da1, da2, da3, da4, da5 = runExp(root, prj, id, 'dev')
        # ra1, ra2, ra3, ra4, ra5 = runExp(root, prj, id, 'randoop')

        # Add the APFD values into their list to produce the box plots
        if da4 < 1:
            bytecodeAPFD.append( round(da4*100, 2) )
        
        # Save the real fault indecies
        bytecodeFDRace.append( realFaultRace['diversity'])
        
    # except:
    #     print('Project ' + str(id) + ' failed to run properly')

msplotFile = root + '/PlotGeneration/after-coverage/' + prj + '/' + prj + '-APFD.py'
realfaultplotFile = root + '/PlotGeneration/after-coverage/' + prj + '/' + prj + '-realfault.py'
dstPlot = root + '/resources/plots/' + prj
createFolder(root + '/resources/plots/')
print('APFD = ', bytecodeAPFD)

print('Realfault race = ', bytecodeFDRace)

print(', '.join('{:0.2f}'.format(i) for i in times))
