#!/bin/sh
# package repository updates

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

if [ -d ${t} ]
then
  echo "Time directory already exists. Repo already created?"
  echo "Remove to recreate"
  exit 1
fi

i=0
while [ $i -lt ${#reposync[@]} ] 
do

  repo=`echo ${reposync[$i]} | sed 's/\(.*\)-reposync.log/\1/g' | sed 's/[0-9]*-\(.*\)/\1/g'`
  
  echo "Processing repo ${repo}"
  
  tmp=`mktemp`
  
  errors=`mktemp`
  grep Error ${t}-${repo}-reposync.log > $errors
  
  for f in `cat ${t}-${repo}-reposync.log | grep Downloading | awk '{print $7}'`
  do
    f=`basename $f`
    
    egrep -q "Error.*/$f" $errors
    if [ $? -eq 0 ]
    then
      if [ -f ERRORS/${t}/${repo}/Packages/$f ]
      then
        echo "Error file already removed $f"
        continue
      fi
      echo "  $f ERROR downloading"
      if [ -f ${repo}/Packages/${f} ]
      then
        mkdir -p ERRORS/${t}/${repo}/Packages/
        mv ${repo}/Packages/${f} ERRORS/${t}/${repo}/Packages/
        echo "Archived to ERRORS/${t}/${repo}/Packages/$f"
      fi
      continue
    fi
    
    if [ ! -s ${repo}/Packages/${f} ]
    then
      echo "  $f ERROR 0 size"
      mkdir -p ERRORS/${t}/${repo}/Packages/
      mv ${repo}/Packages/${f} ERRORS/${t}/${repo}/Packages/
      echo "Archived to ERRORS/${t}/${repo}/Packages/$f"
      continue
    fi
        
    dest=${t}/${repo}
    mkdir -p ${dest}
    
    cp ${repo}/Packages/${f} ${dest}
    
    if [ $? -eq 0 ]
    then
      echo "  $f"
    else
      echo "  Unable to copy: $f"
    fi
  done
  
  echo

  rm ${tmp}
  
  i=`expr $i + 1`
done

echo "Created diff package ${t}/"
cd ${t}
du -hsc *

echo "Next, run './package-tar.sh ${t}'"

