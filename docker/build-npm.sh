#!/bin/bash

arg=$1

#if [ -z "$PLATFORM" ] ; then
#    echo "Error, you must specify target platform into PLATFORM environment" >&2
#    exit 1
#fi

case $arg in
    meta)

        version=$(make version)
        if [ -z "$version" ] ; then
            version=$(cat package.json | jq ".version" | sed 's/\"//g')
        fi
        echo "{\"version\": \"$version\"}"
    ;;
    *)

        if [ -d npm/hooks ] ; then
            for file in npm/hooks/* ; do
                sh $file
            done
        fi

        if [ -f Makefile ] ; then
            make
        else
            npm run build
            npm pack
        fi
        mv *.tgz /build/binary/
    
    ;;
esac