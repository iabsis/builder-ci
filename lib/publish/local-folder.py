#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Publish any files into a folder on your build server
"""

import os
import io
import re
import config
import logs
import glob
import shutil
import traceback

build_location = config.getSection("default")["build_location"]
pwd = os.getcwd()

method = {
    "name": "local-folder",
    "meta": []
}

def runAction(id, options, meta):

    project_path = os.path.join(build_location, id)
    sources_path = os.path.join(pwd, build_location, id, "sources")
    binary_path = os.path.join(build_location, id, "binary")

    source_files = options["source_files"]
    target_path = options["target_path"]
    repo_path = os.path.join(options["default_target"], meta["name"])
    base_target = os.path.join(options["default_target"], meta["name"], target_path)

    try:
        os.makedirs(base_target)
    except FileExistsError:
        logs.debug("Target folder already exists")
        pass

    logs.debug(binary_path + "/" + source_files)

    try:
        for file in glob.glob(binary_path + "/" + source_files):
            logs.debug("Moving file: " + file)
            shutil.move(file, base_target)
    except:
        log_err = traceback.format_exc()
        
        return [False, log_out, log_err]

    return [True, None, None]

def getMeta(id, options, meta):
    return None


def detect(id, options, meta):
    return False