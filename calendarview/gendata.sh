#!/bin/bash

NOW=`date +%s`

while getopts "Hs:m:h:d:w:m:y:" opt
do
  case $opt in
    H) echo "datetime,category,subcategory,amount"; exit 0;;
    s) NOW=$(( $NOW - $OPTARG ));;
    m) OFFSET=$(( $OPTARG * 60 )); NOW=$(( $NOW - $OFFSET ));;
    h) OFFSET=$(( $OPTARG * 3600 )); NOW=$(( $NOW - $OFFSET ));;
    d) OFFSET=$(( $OPTARG * 86400 )); NOW=$(( $NOW - $OFFSET ));;
    w) OFFSET=$(( $OPTARG * 604800 )); NOW=$(( $NOW - $OFFSET ));;
    m) OFFSET=$(( $OPTARG * 2592000 )); NOW=$(( $NOW - $OFFSET ));;
    y) OFFSET=$(( $OPTARG * 31536000 )); NOW=$(( $NOW - $OFFSET ));;
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


AMT=$(( ( RANDOM % 100 )  + 1 ))
CAT=${CATEGORIES[$(( RANDOM % ${#CATEGORIES[@]} ))]}

# get subcat array variable from indirect reference
eval SUBCATEGORIES=\( \${$CAT[@]} \)
SUBCAT=${SUBCATEGORIES[$(( RANDOM % ${#SUBCATEGORIES[@]} ))]}

echo $NOW,$CAT,$SUBCAT,$AMT

