#!/bin/sh -x

if [ $# -le 1 ]
then
  echo "`basename $0` repo [options] package[s]"
  echo
  echo "Must provide a repository and package name" 
  echo
  echo "Some useful options:"
  echo "  --destdir=<path> : specify download path. Default cwd"
  echo "  --archlist=<arch> : specify CPU architecture"
  echo "  --source : get source packages"
  echo "  --config=<cfg> : specify repo configuration file"
  exit 1
fi

if [ -z "`which yumdownloader`" ]
then
  echo "Requires yumdownloader"
  echo "yum install yum-utils"
  exit 1
fi

REPO=$1
shift

yumdownloader --disablerepo=\* --enablerepo=$REPO --resolve $*
exit $?


