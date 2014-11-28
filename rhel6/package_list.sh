#!/bin/sh

if [ $# -eq 0 ]
then
  echo "`basename $0` packages"
  echo 
  echo "List packages from various repositories"
  exit 1
fi

PACKS=( $* )

for f in *.repo
do
  r=`echo $f | awk -F. '{print $1}'`

  yum --config $f --enablerepo=\* list ${PACKS[@]} 2> /dev/null
  if [ $? -ne 0 ]
  then
    echo Repository $r failed
  fi

done

