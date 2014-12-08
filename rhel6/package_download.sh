#!/bin/sh

usage() {
  echo "`basename $0` -r repo [options] -p package"
  echo
  echo "Download packages and maintain repositories"
  echo "Must provide a repository and at least one package name" 
  echo
  echo "Options:"
  echo -e "  -r repo\tRepository to get packages from"
  echo -e "  -d dir\tDirectory to write packages"
  echo -e "  -a arch\tSpecify platform architecture"
  echo -e "  -c cfg\tYum configuration file"
  echo -e "  -p pack\tRPM package to download"
  echo -e "  -R\t\tAlso download required dependencies"
  echo -e "  -S\t\tDownload source packages"
}

if [ -z "`which yumdownloader`" ]
then
  echo "Requires yumdownloader"
  echo "yum install yum-utils"
  exit 1
fi

if [ -z "`which createrepo`" ]
then
  echo "Requires createrepo"
  echo "yum install createrepo"
  exit 1
fi

PACKS=( )
REPOS=( )
ARCH=
CONFIGS=( )
SOURCE=0
REQUIRES=0
DESTDIR=

while getopts "hSRd:a:c:r:p:" opt; do
  case $opt in
    h) usage; exit 0;;
    p) PACKS=( ${PACKS[@]} $OPTARG );;
    r) REPOS=( ${REPOS[@]} $OPTARG );;
    c) CONFIGS=( ${CONFIGS[@]} $OPTARG );;
    a) ARCH=$OPTARG;;
    d) DESTDIR=$OPTARG;;
    S) SOURCE=1;;
    R) REQUIRES=1;;
    *) usage; exit 1;;
  esac
done

if [[ ${#REPOS[@]} -eq 0 || ${#PACKS[@]} -eq 0 ]]
then
  echo "Must provide at least one repository and one package"
  echo 
  usage
  exit 1
fi

# BUILD ARGS FOR DOWNLOADING PACKAGES

OPTS="--disablerepo=*"

for c in ${CONFIGS[@]}
do
  OPTS="$OPTS --config=$c"
done

for r in ${REPOS[@]}
do
  OPTS="$OPTS --enablerepo=$r"
done

if [ -n "$ARCH" ]
then
  OPTS="$OPTS --archlist=$ARCH"
fi

if [ -n "$DESTDIR" ]
then
  OPTS="$OPTS --destdir=$DESTDIR"
fi

if [ $REQUIRES -eq 1 ]
then
  OPTS="$OPTS --resolve"
fi

if [ $SOURCE -eq 1 ]
then
  OPTS="$OPTS --source"
fi

for p in ${PACKS[@]}
do
  OPTS="$OPTS $p"
done

yumdownloader $OPTS 2>&1 | tee log
yumdlexit=$?

echo YUMDL $yumdlexit

if [[ $yumdlexit -eq 0 && -n "$DESTDIR" ]]
then
  createrepo $DESTDIR
fi

if [ $SOURCE -eq 0 ]
then
  exit $yumdlexit
fi

# TODO CONTINUE TO DOWNLOAD SOURCE PACKAGES
# Using yum-builddep get dependencies for building src.rpms

exit $yumdlexit
















