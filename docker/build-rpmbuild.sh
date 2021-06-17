#!/bin/bash

arg=$1

if [ -z "$SPEC_PATH" ] ; then
    echo "Error, you must specify spec path into SPEC_PATH environment" >&2
    exit 1
fi

case $arg in
    meta)

        arch=$(cat "$SPEC_PATH" | grep -i "BuildArch:" | head -n 1 | cut -f 2 -d' ')
        versionShort=$(cat "$SPEC_PATH" | grep -i "Version:" | head -n 1 | cut -f 2 -d' ')
        revision=$(cat "$SPEC_PATH" | grep -i "Release:" | head -n 1 | cut -f 2 -d' ')
        [ -z $versionShort ] && versionShort=undefined
        [ -z $revision ] && revision=undefined
        [ -z $arch ] && arch=undefined
        version=${versionShort}-${revision}
        dist=$(cat /etc/os-release | grep ^VERSION= | cut -f2 -d\")
        echo "{\"version\": \"$version\", \"arch\": \"$arch\", \"dist\": \"$dist\"}"
    ;;
    *)

        # Run hooks
        if [ -d redhat/hooks ] ; then
            for file in redhat/hooks/* ; do
                sh $file
            done
        fi

        yum-builddep -y $SPEC_PATH
        /usr/bin/rpmbuild -bb $SPEC_PATH --define "_sourcedir $PWD"

        mkdir -p /build/binary/
        mv /root/rpmbuild/RPMS/*/*.rpm /build/binary/
    
    ;;
esac