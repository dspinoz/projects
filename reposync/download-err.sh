#!/bin/sh
# check a series of logs for errors and attempt to redownload the packages

if [ -z "$*" ]
then
  echo "Provide a timestamp update list"
  exit 1
fi

t=$1
num=`ls ${t}*-reposync.log | wc -l`
if [ $num -eq 0 ]
then
  echo "Timestamp does not have reposync files"
  exit 1
fi

reposync=( ${t}*-reposync.log )

echo "Inspecting logs ${reposync[@]}"

packs=( )

for pack in `cat ${reposync[@]} | grep Error | sed 's%.*Error was failure: Packages/\(.*\?\) from \(.*\?\): .*%\1%g' | grep -v Skipping | xargs`
do
  # dont have the package, cannot query with rpm
  #rpm --query --queryformat "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\n" --package $repo/Packages/$pack
  
  # search the output from download.sh
  # download.sh guarantees that if the file is there is has successfully been downloaded
  got=( `ls *-download/${pack} 2> /dev/null` )
  
  if [ ${#got[@]} -eq 0 ]
  then
    pack=`echo $pack | sed 's/\(.*\).rpm/\1/g'`
    packs=( ${packs[@]} $pack )
  else
    echo "Already downloaded $pack : ${got[@]}"
  fi
done

if [ ${#packs[@]} -le 0 ]
then
  echo "No packages to download for $t"
  exit 0
fi

echo "Redownload ${#packs[@]} packages ? y/n"
read ans
if [ $ans != "y" ]
then
  echo "Cancelled"
  exit 0
fi

./download.sh ${packs[@]}


