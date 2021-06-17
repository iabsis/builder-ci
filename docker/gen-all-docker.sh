#!/bin/bash

for file in *; do
    if [ -d $file ] ; then
        docker build -t $file -f $file/Dockerfile .
    fi
done