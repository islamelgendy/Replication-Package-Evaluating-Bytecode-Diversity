import os
import tarfile
import time
import sys
from utils.utilsIO import *
from utils.utilsSystem import *
from utils.pomModify import *

#project = input("Enter project id: ")
args = sys.argv
if len(args) == 1:
    project = "collections"
else: 
    project = args[1]

#print(args)

lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]

folder = root + "/scripts/tests/" + project + "-tests"

# Loop through all files in the directory of the project and store the compressed files in a list
compressedfiles = getAllFilesEndingWith(folder, '.tar.bz2')

versionsIncluded = []
versionsNotIncluded = []
fuckedupVersions = []

# Loop through all compressed files
for compressedFile in compressedfiles:
    # Read the compressed file and extract it at the same path
    tar = tarfile.open(compressedFile, "r:bz2")  

    # Get parent directory of file
    parent = os.path.dirname(compressedFile)

    # Extract the contents in the same directory of the file
    tar.extractall(parent)
    tar.close()

    # Extract all relevant information from the filename
    pid,vid,tool = extractInfo(compressedFile)

    if tool == 'randoop':
        debug = True

    # Get all java files from the extracted files
    javaFiles = getAllFilesEndingWith(parent,'.java')

    # Extract the package line to identify where to copy the files
    # jFile = open(javaFiles[0], 'r')
    packageLine = getPackageLines(javaFiles)
    # print("First line",packageLine)

    # curDir = '../resources/subjects/buggy/' + project + '/' + vid
    
    # Checkout that buggy version
    g, curDir = checkoutVersion(pid, vid, root + '/resources/subjects/buggy/' + project, False)

    if not modifyPom(curDir+'/pom.xml'):
        fuckedupVersions.append(vid)
        continue

    # Build the proper path to where files should be copied at
    testpaths, signatures = getFolder(packageLine)

    testDirs = set()
    for testpath in testpaths:
        testDir = curDir + '/src/test/java' + testpath
        testDirs.add(testDir)

    # Copy the java files into the test folder in their proper place
    if not copyFiles(javaFiles,testDirs, tool):
        fuckedupVersions.append(tool + '-' + vid)
        continue

    # Run the extracted test files against the checkedout buggy version
    # if runBuggyVersion(curDir,javaFiles,signatures,tool):
    versionsIncluded.append(tool + '-' + vid)

    fixedVersionPath = root + '/resources/subjects/fixed/' + project + '/' + vid
    # If the fixed version already checked out, don't check it out again (this will delete any copied test files that were added)
    if not os.path.isdir(fixedVersionPath):
        # Checkout the fixed version
        g, fixDir = checkoutVersion(pid, vid, root + '/resources/subjects/fixed/' + project, True)
    else:
        fixDir = root + '/resources/subjects/fixed/' + project + '/' + vid

    # Find out the modified classes
    tarClasses, testClasses, trigerClass = getTargetAndTestClasses(fixDir)

    # Modify the pom file of the fixed version to add plugins for Jacoco, PIT, and javaAssist. Also to generate byte code of the tests
    modifyPom(fixDir+'/pom.xml', True, tarClasses, testClasses)

    # Copy test files into the fixed version
    testDirs = set()
    for testpath in testpaths:
        testDir = fixDir + '/src/test/java' + testpath
        testDirs.add(testDir)
    copyFiles(javaFiles,testDirs, tool)
        
    # else:
    #     versionsNotIncluded.append(tool + '-' + vid)

    # Deleted the extracted files to save space
    deleteFolders(parent)

    time.sleep(1)

print('Versions to include', versionsIncluded)
print('fucked up versions', fuckedupVersions)
print('Versions to exclude', versionsNotIncluded)