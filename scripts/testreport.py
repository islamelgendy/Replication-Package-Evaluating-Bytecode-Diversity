import os
import javalang
import sys
from utils.mutationxml import parseMutationsXML
from utils.pomModify import getTargetAndTestClasses
from utils.utilsIO import *
from utils.utilsSystem import createFolder, runMavenTest, runSingleTestMethod, runMutation, getBytecodeFile
from utils.jacocohtmlParser import *
from utils.CoverageLineInfo import *
from utils.testMethod import *

def addPartialRecord(partialRecord, record):
    if partialRecord == '':
        partialRecord += record
    else:
        firstCommaPos = record.index(',')
        partialRecord += record[firstCommaPos:]
    
    return partialRecord

def findSuperClassExtendsTestCase(javaTestFiles, superClass):
    superTestFile = None
    for file in javaTestFiles:
        if file.endswith(superClass + '.java'):
            superTestFile = file
            break

    if not superTestFile:
        return False
    
    with open(superTestFile, "r") as f:
        contents = f.readlines()

    testFileStr = "".join(contents)

    tree = javalang.parse.parse(testFileStr)

    packagename = tree.package.name

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        classname = node.name
        if not node.extends == None:
            superClass = node.extends.name
            if superClass == 'TestCase':
                return True
            else:
                return findSuperClassExtendsTestCase(javaTestFiles, superClass)
        else:
            return False
         
    return False

def checkProject(root, folder, project, id):
    # check if that previous reports exist
    similarityFile = root + "/resources/similarity/" + project + "/" + project + '.' + id + 'f.test-cases.txt'
    mutationFile = root + "/resources/mutation/" + project + "/" + project + '.' + id + 'f.mutation.csv'
    statmentCoverageFile = root + "/resources/coverage/" + project + "/" + project + '.' + id + 'f.statement.coverage.csv'
    branchCoverageFile = root + "/resources/coverage/" + project + "/" + project + '.' + id + 'f.branch.coverage.csv'

    if os.path.isfile(similarityFile) or os.path.isfile(mutationFile) or os.path.isfile(statmentCoverageFile) or os.path.isfile(branchCoverageFile):
        return True, similarityFile, statmentCoverageFile, branchCoverageFile, mutationFile

    else:
        # First test if mutation can be performed, if not end the program
        # Run the mutation for the current project
        print("Running mutation.................................", end="", flush=True)
        try:
            mutationOutputFile = runMutation(root, folder, project)
            if processMutationOutput(folder, mutationOutputFile):
                print("OK")
                return False, similarityFile, statmentCoverageFile, branchCoverageFile, mutationFile
            else:
                print("Mutation failed, and no need to continue the analysis")
                os._exit(1)
        except:
            print("failed")
            os._exit(1)
    
#project = input("Enter project id: ")
args = sys.argv
if len(args) == 1:
    project = "compress"
    id = "6"
else: 
    project = args[1]
    id = args[2]

print(args)

lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]

print (root)

folder = root + "/resources/subjects/fixed/" + project + "/" + id
fixedfolder = root + "/resources/subjects/fixed/" + project + "/" + id
buggyfolder = root + "/resources/subjects/buggy/" + project + "/" + id

if not os. path. isdir(folder):
    print(folder + ' does not exist')
    sys.exit(1)
# Find out the modified classes
tarClasses, testClasses, trigerClasses = getTargetAndTestClasses(folder)

# set the path for the Jacoco html files
jacocoPath = folder + '/target/site/jacoco/'

# set the path for PIT XML files
mutationsFile = folder + '/target/pit-reports/mutations.xml'

# set the path for the bytecode classes
bytecodePath = folder + '/target/test-classes/'

# Get the bytecode test files
# Loop through all files in the test directory of the project and store the bytecode files in a list
print("Running tests on fixed version.................................", end="", flush=True)
runMavenTest(root, fixedfolder)
print("OK")
javaBytecodeFiles = getAllFilesEndingWith(bytecodePath, '.class')

# First test if mutation can be performed, if not end the program
# Also, check if that project was previously half analysed and needs to continue
isPartial, similarityFile, statmentCoverageFile, branchCoverageFile, mutationFile = checkProject(root, folder, project, id)

# ClassDeclaration: gets all classes
# MethodDeclaration: gets all methods
# ConstructorDeclaration: gets all constructors
# FieldDeclaration: gets all fields

# Loop through all files in the test directory of the project and store the java files in a list
javaTestFiles = getAllFilesEndingWith(folder + "/src/test/java", '.java')

# brenttestfile = javaTestFiles[145]
# testfile = javaTestFiles[14]

# For each html/class prepare a CSV (a list of list of strings)
csvStatementList = list()
csvBranchList = list()

# Identify the right HTML files
# For each targetClass find the HTML file to parse
htmlFiles = list()

for tarClass in tarClasses:
    targetClassName = re.split('\.', tarClass)[-1]
    lastDotPos = tarClass.rfind('.')
    packagename = tarClass[0:lastDotPos]
    htmlFiles.append(jacocoPath + packagename + '/' + targetClassName + '.java.html')
    
    #Add a csv contents for this htmlFile
    csvStatementFile = CSV_HTML()
    csvStatementFile.setFilePath(jacocoPath + packagename + '/' + targetClassName + '.java.html')
    csvStatementFile.setFileName(targetClassName)
    csvStatementList.append(csvStatementFile)
    csvBranchFile = CSV_HTML()
    csvBranchFile.setFilePath(jacocoPath + packagename + '/' + targetClassName + '.java.html')
    csvBranchFile.setFileName(targetClassName)
    csvBranchList.append(csvBranchFile)

# Set the list of methods to be loaded
listTestMethods = list()
newMethods = list()
# This project needs to continue on before
# isPartial = False
if isPartial:
    # get all previous methods from similarity file
    listTestMethods = loadTestcases(folder, project, id, similarityFile)
    for testMtd in listTestMethods:
        if '_ESTest::test' in testMtd.methodName or ('::test' in testMtd.methodName and testMtd.methodName.startswith('RegressionTest')):
            continue
        elif len(testMtd.body) == 0:
            continue
        testMtd.fixTestcase()

    csvTextSimPath = root + "/resources/similarity/" + project + "/" + project + "." + id + "f.test-cases.txt"
    createFolder(root + "/resources/similarity/" + project)
    writeTestCasesToFile(listTestMethods, csvTextSimPath, False)

# sys.exit() 

newTestsTextSimPath = root + "/resources/similarity/" + project + "/" + project + "." + id + "f.new-test-cases.txt"
createFolder(root + "/resources/similarity/" + project)

# check if realfaults already there
csvFaultsDetectedPath = root + "/resources/realfault/" + project + "." + id + "f.realfaults-detected.csv"
if not os.path.isfile(csvFaultsDetectedPath):
    # Check if the test reveals the real fault
    # Run the method on the buggy version
    print("Running tests on buggy version.................................", end="", flush=True)
    runMavenTest(root, buggyfolder)
    print("OK")

    outputfile = buggyfolder + '/output-details/output-all.txt'

    # Check the outputfile, if there are any errors or faults, then the method detects the error
    failingMethods = processMavenOutputAndParseFailedMethods(outputfile)

    # Write the methods detecting the real faults
    print("Write tests detecting real faults.............................", end="", flush=True)

    writeOnlyFaultDetectingMethodsToFile(failingMethods, csvFaultsDetectedPath)
    print("OK")

# Loop through the test files
for testfile in javaTestFiles:
    # Flag for junit 3
    Junit3 = False

    # For speedup, check if this test file is worth looking into
    if not isRightTestFile(testfile, tarClasses, trigerClasses, False):
        continue

    with open(testfile, "r") as f:
        contents = f.readlines()

    testFileStr = "".join(contents)

    tree = javalang.parse.parse(testFileStr)

    packagename = tree.package.name

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        classname = node.name
        if not node.extends == None:
            superClass = node.extends.name
            if superClass == 'TestCase':
                Junit3 = True
            elif findSuperClassExtendsTestCase(javaTestFiles, superClass):
                Junit3 = True
        else:
            Junit3 = False
        break 

    # Get the exact bytecode test class file by matching it against the testfile
    bytecodeFile = getBytecodeFile(javaBytecodeFiles, classname, packagename)

    # Print working test class
    print("Running " + classname + ".................................", end="", flush=True)

    # Gets all methods in the class
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        methodName = node.name
        annotations = node.annotations

        if (len(annotations) and node.annotations[0].name == 'Test') > 0 or (Junit3 and checkNode(node)):
            # annotation = node.annotations[0].name

            # If that method is already in a previous analysis, skip it
            if checkMethod(listTestMethods, classname, methodName):
                continue

            runSingleTestMethod(root, folder,packagename, classname, methodName)

            outputfile = folder + '/output-details/output-' + str(packagename + '.' + classname) + '-' + str(methodName) + '.txt'

        else:
            continue

        try:
            # Check if this test failed. If so, then it is flaky, and need to be removed
            fails, errors = processMavenOutput(outputfile)
            
            # If it fails, skip it to the next test
            if fails > 0 or errors > 0:
                # Delete that flaky test from the test file
                deleteFlakeyTest(testfile, methodName)
                continue
        except:
            print('Error processing the test output of %s method', methodName)
            # Delete that flaky test from the test file
            deleteFlakeyTest(testfile, methodName)
            continue

        # Load that test method
        methodStartLine = node.position.line - 1
        testMethod = TestMethod(testfile, bytecodeFile, classname, methodName, methodStartLine)
        if isPartial:
            # Save the newly added test methods to a file so similarity calculation can resume
            writeNewTestsToFile(testMethod.methodName + '\n', newTestsTextSimPath)
            appendTestCaseToFile(testMethod, similarityFile)
        else:
            listTestMethods.append(testMethod)
       
        # Go through the html files and start parsing them
        partialStatementRecord = ''
        partialBranchRecord = ''
        for htmlFile in htmlFiles:
            # Identify the csv list for that html file
            # Need to get the index
            index = findIndexOfHTMLFile(csvStatementList, htmlFile)

            try:
                infoList = processHTML(htmlFile)
            except:
                # If the html file is not generated from Jacoco, just skip it
                continue
        
            if len(csvStatementList[index].csvContents) == 0:
                statementHeader, branchHeader = getHeader(infoList)
                csvStatementList[index].addLine( statementHeader + '\n')
                csvBranchList[index].addLine( branchHeader + '\n')
                # headerLine = False
            
            statementRecord, branchRecord = getMethodCoverageRecord(classname, methodName, infoList)
            
            csvStatementList[index].addLine( statementRecord + '\n')
            partialStatementRecord = addPartialRecord(partialStatementRecord, statementRecord)
            csvBranchList[index].addLine( branchRecord + '\n')
            partialBranchRecord = addPartialRecord(partialBranchRecord, branchRecord)
        
        if isPartial:
            appendToFile(statmentCoverageFile, partialStatementRecord + '\n')
            appendToFile(branchCoverageFile, partialBranchRecord + '\n')

    print("OK")

if not isPartial:
    # Calculate the similarity values and output into CSV file
    # print("Calculating textual similarity.................................", end="")
    print("Saving test cases for later.................................", end="", flush=True)
    # simMat = getSimilarityMatrix(listTestMethods)


    # csvTextSimPath = root + "/resources/similarity/" + project + "." + id + "f.textSimilarity.csv"
    csvTextSimPath = root + "/resources/similarity/" + project + "/" + project + "." + id + "f.test-cases.txt"
    createFolder(root + "/resources/similarity/" + project)
    writeTestCasesToFile(listTestMethods, csvTextSimPath)
    print("OK")

    # csvFaultsDetectedPath = root + "/resources/realfault/" + project + "." + id + "f.realfaults.csv"
    # writeFaultDetectionToFile(listTestMethods, failingMethods, csvFaultsDetectedPath)

    # Write down the contents into CSV file
    # for csvFileContents in csvStatementList:
    #     csvfilePath = "../resources/coverage/" + project + "." + id + "f." + csvFileContents.htmlFileName + ".statement.coverage.csv"
    #     writeContentsToFile(csvFileContents, csvfilePath)

    createFolder(root + "/resources/coverage/" + project)
    csvfilePath = root + "/resources/coverage/" + project + "/" + project + "." + id + "f." + "statement.coverage.csv"
    mergeCSVFiles(csvStatementList, csvfilePath)

    # for csvFileContents in csvBranchList:
    #     csvfilePath = "../resources/coverage/" + project + "." + id + "f." + csvFileContents.htmlFileName + ".branch.coverage.csv"
    #     writeContentsToFile(csvFileContents, csvfilePath)

    csvfilePath = root + "/resources/coverage/" + project + "/" + project + "." + id + "f." + "branch.coverage.csv"
    mergeCSVFiles(csvBranchList, csvfilePath)
# elif newMethods:
#     #Save the newly added test methods to a file so similarity calculation can resume
#     newTestsTextSimPath = root + "/resources/similarity/" + project + "/" + project + "." + id + "f.new-test-cases.txt"
#     createFolder(root + "/resources/similarity/" + project)
#     writeNewTestsToFile(newMethods, newTestsTextSimPath)

# Run the mutation for the current project
print("Running mutation.................................", end="", flush=True)
try:
    mutationOutputFile = runMutation(root, folder, project)
    print("OK")
except:
    print("failed")

# Parse the mutation file
createFolder(root + "/resources/mutation/" + project)
csvfilePath = root + "/resources/mutation/" + project + "/" + project + "." + id + "f." + "mutation.csv"
parseMutationsXML(mutationsFile, csvfilePath)