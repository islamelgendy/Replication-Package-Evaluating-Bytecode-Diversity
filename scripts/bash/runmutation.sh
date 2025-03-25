#!/bin/bash         

path=$1
project=$2


cd $path

mkdir -p output-mutation

mvn test-compile org.pitest:pitest-maven:mutationCoverage > output-${project}.txt

mv output-${project}.txt ./output-mutation

