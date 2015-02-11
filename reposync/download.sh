#!/bin/sh -x
# download packages

ARGS=( $* )

which yumdownloader > /dev/null

if [ $? -eq 1 ]
then
  echo "Installing yumdownloader..."
  yum install yum-utils
fi

echo "${ARGS[@]}" | grep -q "\\-h "
if [ $? -eq 0 ]
then
  yumdownloader -h
  exit 0
fi



time=`date +%s`
LOG=`pwd`/${time}-download.log

echo "determining package urls..." >> $LOG
yumdownloader --cacheonly --urls $* 2>&1 | tee -a ${LOG} > /dev/null

grep -q "Nothing to download" $LOG
if [ $? -eq 0 ]
then
  echo "yumdownloader: Nothing to download"
  exit 1
fi

mkdir ${time}-download
pushd ${time}-download

echo "downloading..." >> ${LOG}
yumdownloader --cacheonly $* 2>&1 | tee -a ${LOG}

echo "yumdownloader: return code $?" | tee -a ${LOG}

popd

echo "downloaded:" >> ${LOG}
find ${time}-download -type f -name '*.rpm' | sed "s%${time}-download/%  %g" | tee -a ${LOG}

# look for errors
for pack in `cat ${LOG} | grep 'Could not download' | sed 's%Could not download.*Packages/\(.*\) from \(.*\?\):.*%\1%g' | xargs`
do
  echo "ERROR Downloading $pack"
  if [ ! -f ${time}-download/${pack} ]
  then
    echo "WHERE IS IT!?"
  else
    rm ${time}-download/${pack}
  fi
  
done

echo "GOT `find ${time}-download/ -type f | wc -l` files"

if [ `find ${time}-download/ -type f | wc -l` -eq 0 ]
then
  rm -rf ${time}-download
  exit 1
fi

exit 0


echo "moving files to appropriate directories"

for url in `cat ${LOG} | grep https `
do
  dir=`echo $url | awk -F/ '{print $6"-"$8"-"$7"-"$11"-"$12"-rpms"}'`
  file=`echo $url | sed 's^.*/\(.*\)$^\1^g'`
  
  dir="$dir/Packages"
  
  if [ ! -d $dir ]
  then
    mkdir -p $dir
  fi
  
  echo "moving $file to `dirname $dir`"
  
  mv $file $dir/
  
done
