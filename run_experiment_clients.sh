#!/bin/bash

if [ -z "$1" ]
  then
    echo "Please supply QOS"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "Please supply docker stats file name"
    exit 1
fi


export QOS=$1

echo "Running clients for QOS: $1 and saving docker stats in $2"

sh record_stats.sh $2 > /dev/null 2>&1 &

docker compose -f docker-compose-clients up &






