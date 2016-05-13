#!/bin/bash

DAYS=-365

./gendata.sh -H > transactions.csv

while [ $DAYS -lt 10 ]
do
  ./gendata.sh -d $DAYS $* >> transactions.csv
  echo -n $DAYS >&2
  ((DAYS++))
done



