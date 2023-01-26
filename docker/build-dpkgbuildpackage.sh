#!/bin/bash

set +e

arg=$1

apt update

case $arg in
    meta)

        version=$(head -n 1 debian/changelog | cut -d\( -f 2 | cut -d\) -f 1)
        dist=$(cat /etc/os-release | grep ^VERSION_CODENAME= | cut -f2 -d\=)
        echo "{\"version\": \"$version\", \"dist\": \"$dist\", \"arch\": \"amd64\"}"
    ;;
    *)

        # Run hooks
        if [ -d debian/hooks ] ; then
            for file in debian/hooks/* ; do
                sh $file
            done
        fi

	    apt-get update
        mk-build-deps -r -i -t "apt-get -y -o Debug::pkgProblemResolver=yes --no-install-recommends"
        rm -f *build-deps*
        dpkg-buildpackage

        mkdir -p /build/binary/
        find ../ -type f -maxdepth 1 | while read file; do
            mv $file /build/binary/
        done
    
    ;;
esac
