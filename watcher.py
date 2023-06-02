#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('lib')
from time import sleep

import config
run_every = config.getAttribute("watcher", "run_every")

import db
import importlib
import logs
from json import dumps, loads


def isBuilt(name, version):
    request = {
        "project": name,
        "patcher" : {
            "method": "debian_version",
            "options": {
                "version": version
            }
        }
    }
    return db.isExistBuild(request)

def updateVersion(build, version):
    new_dump = dumps(build).replace(":version", version)
    return loads(new_dump)


if __name__ == "__main__":

    while True:
        for project in db.getWatches():
            try:
                method = project["watch"]["method"]
                options = project["watch"]["options"]
                name = project["project"]
                build = project["build"]
                build["project"] = name
                lib = f"lib.watcher.{method}"
                method = importlib.import_module(lib)
            except KeyError as e:
                logs.error(f"Error loading method with missing key: {e}")
                continue
            
            version = method.getLastVersion(id, options)["version"]
            
            if isBuilt(name, version):
                logs.debug(f"Build for project {name} and version {version} already exists")
                continue
            
            logs.info(f"Automatically added project {name} and version {version} into build queue")
            
            build = updateVersion(build, version)
            db.addBuild(build)
        
        sleep(int(run_every)*60)