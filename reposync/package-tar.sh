#!/bin/sh
# package repository updates ready for transfer

if [ -z "$*" ]
then
  echo "Provide a timestamp update list"
  exit 1
fi

t=$1

if [ ! -d ${t} ]
then
  echo "Time directory does not exist. Create it with package.sh" 
  exit 1
fi

cd ${t}

for dir in *
do

  tar cvf - ${dir} | split --bytes=174m --suffix-length=4 --numeric-suffix - ../${t}-${dir}.tar.

done

du -hsc ../${t}*.tar*



