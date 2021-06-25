#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Redhat/Centos repository thanks to createrepo.
"""

import subprocess
import os
import io
import re
import config
import logs
import glob
import shutil

build_location = config.getSection("default")["build_location"]
pwd = os.getcwd()

method = {
    "bin": "createrepo",
    "name": "createrepo",
    "meta": []
}

process = subprocess.Popen(["which", method["name"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    print("ERROR: createrepo is not installed")
    quit()
else:
    createrepo = stdout.splitlines()[0]


def runAction(id, options, meta):

    project_path = os.path.join(build_location, id)
    sources_path = os.path.join(pwd, build_location, id, "sources")
    binary_path = os.path.join(build_location, id, "binary")

    repo_path = os.path.join(options["default_target"], meta["name"])
    base_target = os.path.join(options["default_target"], meta["name"], "redhat")

    try:
        os.makedirs(base_target)
    except FileExistsError:
        logs.debug("Target folder already exists")
        pass

    for file in glob.glob(binary_path + "/*.rpm"):
        logs.debug("Moving file: " + file)
        shutil.move(file, base_target)

    cmd = [  
        createrepo,
        "-q",
        "."
    ]

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
        bufsize=10240,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_target)

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]

def getMeta(id, options, meta):
    return None


def detect(id, options, meta):
    binary_path = os.path.join(build_location + id, "binary")

    ## Define paths
    rpm = glob.glob(os.path.join(binary_path, "*.rpm"))

    if not rpm == []:
        return True