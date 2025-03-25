import os
import time
# from bytecode import BytecodeMethod, find_method_by_name
import sys
from utils.CSVLoader import CSVLoader
from utils.testMethod import *

#project = input("Enter project id: ")
args = sys.argv
if len(args) == 1:
    project = "time"
    id = "13"
    typeSim = 'text'
elif len(args) == 3:
    project = args[1]
    id = args[2]
    typeSim = 'both'
else: 
    project = args[1]
    id = args[2]
    typeSim = args[3]

print(args)

lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]

folder = root + "/resources/similarity/" + project + "/"
csvTextSimPath = folder + project + "." + id + "f.textSimilarity.csv"
csvBytecodeSimPath = folder + project + "." + id + "f.byteCodeSimilarity.csv"
newTestsTextSimPath = root + "/resources/similarity/" + project + "/" + project + "." + id + "f.new-test-cases.txt"
newMethods = None

if not os. path. isdir(folder):
    print(folder + ' does not exist')
    sys.exit(1)

checkTime = True

# Load the test cases from the folder
listTestMethods = loadTestcases(folder, project, id)

if checkTime:
    with open(csvTextSimPath, "r") as f:
        contents = f.readlines()
    if contents[-1].startswith('The time of execution of above matrix is'):
        print(contents[-1])
    else:
        # record start time
        startText = time.process_time()
        # Calculate the similarity values and output into CSV file
        # print("Calculating textual similarity.................................", end="", flush=True)
        simMat = getSimilarityMatrix(listTestMethods)
        # record end time
        endText = time.process_time()
        print(f"Time of {project}_{id} is {(endText-startText)} sec" )
        # print("OK")
    sys.exit(1)




if typeSim == 'both' or typeSim == 'text':

    # Check if there exists a similarity files already or not
    # If so, then use the new test cases to add to the matrix

    if os.path.isfile(csvTextSimPath) and os.path.isfile(newTestsTextSimPath):
        # Load the new test cases' names
        print("Loading new test methods' names.................................", end="", flush=True)
        newMethods = loadNewTestMethods(newTestsTextSimPath)
        print("OK")

        # Load the old similarity csv
        print("Loading old text similarity csv.................................", end="", flush=True)
        simlarityCSV = CSVLoader(csvTextSimPath)
        print("OK")

        # Loop through each new test method, and add a new row and col to the matrix
        print("Calculating textual similarity for new methods..................", end="", flush=True)
        # record start time
        startText = time.process_time()
        simMat = addToSimilarityMatrix(listTestMethods, newMethods, simlarityCSV)
        # record end time
        endText = time.process_time()
        writeSimMatrixToFile(simMat, listTestMethods, csvTextSimPath, (endText-startText))
        print("OK")
    
    else:
        # record start time
        
        # Calculate the similarity values and output into CSV file
        print("Calculating textual similarity.................................", end="", flush=True)
        startText = time.process_time()
        simMat = getSimilarityMatrix(listTestMethods)
        # record end time
        endText = time.process_time()
        writeSimMatrixToFile(simMat, listTestMethods, csvTextSimPath, (endText-startText))
        print("OK")

if typeSim == 'both' or typeSim == 'byte':
    if os.path.isfile(csvBytecodeSimPath) and os.path.isfile(newTestsTextSimPath):
        if not newMethods:
            # Load the new test cases' names
            print("Loading new test methods' names.................................", end="", flush=True)
            newMethods = loadNewTestMethods(newTestsTextSimPath)
            print("OK")
        
        # Load the old similarity csv
        print("Loading old bytecode similarity csv.................................", end="", flush=True)
        simlarityBytecodeCSV = CSVLoader(csvBytecodeSimPath)
        print("OK")

        # Loop through each new test method, and add a new row and col to the matrix
        print("Calculating bytecode similarity for new methods..................", end="", flush=True)
        # record start time
        startText = time.time()
        simMat = addToSimilarityMatrix(listTestMethods, newMethods, simlarityBytecodeCSV, False)
        # record end time
        endText = time.time()
        writeSimMatrixToFile(simMat, listTestMethods, csvBytecodeSimPath, (endText-startText))
        print("OK")
    else:
        # record start time
        startByte = time.time()
        # Calculate the similarity values and output into CSV file
        print("Calculating bytecode similarity.................................", end="", flush=True)
        simByteMat = getSimilarityMatrix(listTestMethods, False)
        # record end time
        endByte = time.time()
        writeSimMatrixToFile(simByteMat, listTestMethods, csvBytecodeSimPath, (endByte-startByte))
        print("OK")

