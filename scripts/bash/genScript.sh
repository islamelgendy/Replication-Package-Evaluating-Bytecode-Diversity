#!/bin/bash         

# Example of a command is:
# ./genScript.sh Jsoup 93 ../tests/jsoup-tests/
export PATH=$PATH:/home/islam/MyWork/Code/defects4j/framework/bin

if [ $# -eq 0 ]
  then
	read -p "Please enter id of project: " id
    	read -p "Please enter max number of versions: " verID
  	read -p "Please enter the root directory: " dir
	
  elif [ $# -eq 1 ]
    then
    	id=$1
    	read -p "Please enter max number of versions: " verID
      read -p "Please enter the root directory: " dir
  elif [ $# -eq 2 ]
    then
      id=$1
      verID=$2
      read -p "Please enter the root directory: " dir
  else
  	id=$1
    verID=$2
    dir=$3
fi

budget1=100
budget2=300

SECONDS=0

for i in $(seq 1 $verID) 
do
    echo "***Working on version ${i}f***"
    now=$(date +"%r")
    echo "Current time : $now"
    
  gen_tests.pl -g "randoop" -p $id -v ${i}f -n $i -o $dir -b $budget1 
  
  gen_tests.pl -g "evosuite" -p $id -v ${i}f -n $i -o $dir -b $budget2 
done

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."

