#!/bin/bash

if [ -z "$1" ]
  then
    echo "Please supply QOS"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "Please supply the log sub path"
    exit 1
fi

if [ -z "$3" ]
  then
    echo "Please supply docker stats file name"
    exit 1
fi

if [ -z "$4" ]
  then
    echo "Please supply the CA cert path"
    exit 1
fi


export QOS=$1

export LOG_PATH=$3

export CERT=$4

echo "Running clients for QOS: $1, log sub path $2 and saving docker stats in $3"

sh record_stats.sh $3 > /dev/null 2>&1 &

docker compose -f docker-compose-clients up &






