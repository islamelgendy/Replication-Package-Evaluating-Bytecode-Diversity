#!/usr/bin/python3

from utils.mutant import Mutant, getCSVKillMap

def parseMutationsXML(xmlFile, csvFile):
    with open(xmlFile, "r") as f:
        contents = f.readlines()

    mutantsList = list()
    # Parse the file line by line
    for i, x in enumerate(contents):
        if x.startswith('<mutation '):
            mut = Mutant()
            
            # Split the packageLine to get the right folder
            mut.parse(x)
            mutantsList.append(mut)

    killMapContents = getCSVKillMap(mutantsList)

    with open(csvFile, "w") as f:
        killMapContents = "".join(killMapContents)
        f.write(killMapContents)


# Testing the code
# xmlFile = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/pit-reports/mutations.xml'
# csvfilePath = "../resources/mutation/time.13f.mutation.csv"

# parseMutationsXML(xmlFile, csvfilePath)