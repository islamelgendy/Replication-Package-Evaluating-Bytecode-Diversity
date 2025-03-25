 #!/bin/bash         

export PATH=$PATH:/home/islam/MyWork/Code/defects4j/framework/bin
export PATH=$PATH:/home/islam/MyWork/Code/defects4j/framework/util

if [ $# -eq 0 ]
  then
	read -p "Please enter the root directory: " dir
	read -p "Please enter id of project: " id
  elif [ $# -eq 1 ]
    then
    	dir=$1
    	read -p "Please enter id of project: " id
  else
  	dir=$1
  	id=$2
fi

cd $dir

SECONDS=0

for i in *
do
    echo "***Working on file $i***"
    now=$(date +"%r")
    echo "Current time : $now"
    fix_test_suite.pl -p $id -d $dir/$i/
  #run_mutation.pl -p $id -d $dir/$i/ -o $dir/$i/
  
  #run_coverage.pl -p $id -d $dir/$i/ -o $dir/$i/
done

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."

