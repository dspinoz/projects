#!/bin/sh -x
# fetch new packages from rhel repositories

shutdown()
{
  exit 1
}
trap shutdown 2

#ifup eth0

#echo $* | grep -q '\-u' 
#if [ $? -eq 0 ]
#then
#yum makecache
#fi

repos=( )
newpackages=( )
reporuntime=( )
now=`date +%s`

#rhel-6-server-supplementary rhel-6-server-optional-rpms  rhel-6-server-rpms 
for repo in rhel-6-server-rpms
do

  startrepo=`date +%s`
  
  # when packaging, error files are removed
  
  ##--newest-only
  reposync  --repoid=$repo 2>&1 | tee ${now}-${repo}-reposync.log | egrep 'Downloading|Error'
  
  donerepo=`date +%s`
  
  new=`cat ${now}-${repo}-reposync.log | grep Downloading | wc -l`
  echo INFO $new new packages in ${repo}
  
  repos=( ${repos[@]} ${repo} )
  newpackages=( ${newpackages[@]} ${new} )
  reporuntime=( ${reporuntime[@]} `expr ${donerepo} - ${startrepo}` )
  
done


echo "-- UPDATE SUMMARY --" | tee -a ${now}.txt
i=0
while [ $i -lt ${#repos[@]} ]
do
  echo "${repos[$i]} - ${newpackages[$i]} new packages (${reporuntime[$i]} runtime)" | tee -a ${now}.txt
  for f in `cat ${now}-${repos[$i]}-reposync.log | grep Downloading | awk '{print $7}'`
  do
    f=`basename $f`
    echo "  ${f}" | tee -a ${now}.txt
  done
  
  grep -q Error ${now}-${repos[$i]}-reposync.log
  if [ $? -eq 0 ]
  then
    echo "Errors downloading:" | tee -a ${now}.txt
    grep Error ${now}-${repos[$i]}-reposync.log | tee -a ${now}.txt
  fi
  
  i=`expr $i + 1`
done
donesync=`date +%s`

if [ 0 -eq 1 ]
then
  echo "-- UPDATING REPO DATA --" 
  i=0
  while [ $i -lt ${#repos[@]} ]
  do
    if [ ${newpackages[$i]} -gt 0 ]
    then
      echo "${newpackages[$i]} new packages for ${repo[$i]}"
      createrepo ${repo[$i]}
    else
      echo "No new packages for ${repo[$i]}"
    fi
    i=`expr $i + 1`
  done
fi
donecreaterepo=`date +%s`

echo "Took `expr $donesync - $now` seconds to sync, `expr $donecreaterepo - $donesync` to createrepo" | tee -a ${now}.txt

for f in `find ${repos[@]} -type f -size 0c`
do
  echo "ERROR file 0 size $f" | tee -a ${now}.txt
done

echo "Next, run './package.sh ${now}'"
