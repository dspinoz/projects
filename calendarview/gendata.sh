#!/bin/bash

NOW=`date +%s`
TYPE=0
MAX=100
MIN=1
AMT=
CAT=
SUBCAT=

while getopts "Hs:m:h:d:w:m:y:t:v:V:c:C:a:" opt
do
  case $opt in
    H) echo "datetime,category,subcategory,amount,type"; exit 0;;
    s) NOW=$(( $NOW - $OPTARG ));;
    m) OFFSET=$(( $OPTARG * 60 )); NOW=$(( $NOW - $OFFSET ));;
    h) OFFSET=$(( $OPTARG * 3600 )); NOW=$(( $NOW - $OFFSET ));;
    d) OFFSET=$(( $OPTARG * 86400 )); NOW=$(( $NOW - $OFFSET ));;
    w) OFFSET=$(( $OPTARG * 604800 )); NOW=$(( $NOW - $OFFSET ));;
    m) OFFSET=$(( $OPTARG * 2592000 )); NOW=$(( $NOW - $OFFSET ));;
    y) OFFSET=$(( $OPTARG * 31536000 )); NOW=$(( $NOW - $OFFSET ));;
    t) TYPE=$OPTARG;;
    v) MAX=$OPTARG;;
    V) MIN=$OPTARG;;
    a) AMT=$OPTARG;;
    c) CAT=$OPTARG;;
    C) SUBCAT=$OPTARG;;
    :) exit 1;;
    \?) exit 1;;
  esac
done

CATEGORIES=( Mum Dad Kid Car Food Out)
Mum=( Clothes )
Dad=( Clothes )
Kid=( Clothes )
Car=( Fuel Insurance Registration )
Food=( Groceries Meat Fish )
Out=( Coffee Breakfast Lunch Dinner Desert )

if [ -z "$AMT" ]
then
  AMT=$(( ( RANDOM % $MAX )  + $MIN ))
fi
  
if [ -z "$CAT" ]
then
  CAT=${CATEGORIES[$(( RANDOM % ${#CATEGORIES[@]} ))]}
fi

if [ -z "$SUBCAT" ]
then
  # get subcat array variable from indirect reference
  eval SUBCATEGORIES=\( \${$CAT[@]} \)
  SUBCAT=${SUBCATEGORIES[$(( RANDOM % ${#SUBCATEGORIES[@]} ))]}
fi

echo $NOW,$CAT,$SUBCAT,$AMT,$TYPE

