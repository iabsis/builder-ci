#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import dumps, loads
import lib.logs as logs
import importlib
import lib.db as db
from time import sleep

from lib.config import Config

config = Config("watcher")

run_every = config["run_every"]


def isBuilt(name, version):
    request = {
        "project": name,
        "patcher": {
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
                logs.debug(
                    f"Build for project {name} and version {version} already exists")
                continue

            logs.info(
                f"Automatically added project {name} and version {version} into build queue")

            build = updateVersion(build, version)
            db.addBuild(build)

        sleep(int(run_every)*60)
