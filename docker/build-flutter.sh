#!/bin/bash

arg=$1

if [ -z "$PLATFORM" ] ; then
    echo "Error, you must specify target platform into PLATFORM environment" >&2
    exit 1
fi

case $arg in
    meta)

        version=$(grep "version:" pubspec.yaml | cut -d' ' -f 2)
        echo "{\"version\": \"$version\"}"
    ;;
    *)

        if [ -d ionic/hooks ] ; then
            for file in ionic/hooks/* ; do
                sh $file
            done
        fi

        make $PLATFORM

        mkdir -p /build/binary/
        mv build/app/outputs/ /build/binary/
    
    ;;
esac