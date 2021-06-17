#!/bin/bash

arg=$1

#if [ -z "$PLATFORM" ] ; then
#    echo "Error, you must specify target platform into PLATFORM environment" >&2
#    exit 1
#fi

case $arg in
    meta)

        version=$(grep "version" package.json | head -n 1 | cut -d\" -f4)
        echo "{\"version\": \"$version\"}"
    ;;
    *)

        if [ -d npm/hooks ] ; then
            for file in npm/hooks/* ; do
                sh $file
            done
        fi

        npm run build
        npm pack
        mv *.tgz /build/binary/
    
    ;;
esac