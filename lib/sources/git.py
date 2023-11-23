#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get source files from git
"""

import subprocess
import os
import tarfile
import io
from lib.config import Config
import shutil
import logs

default_config = Config("default")

build_location = default_config["build_location"]

name = "git"

process = subprocess.Popen(["which", "git"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    print("ERROR: git is not installed")
else:
    gitpath = stdout.splitlines()[0]


def runAction(id, options, meta):
    url = options["url"]
    branch = options["branch"]
    fetch_path = os.path.join(build_location, id, "sources")

    cmd = [
        gitpath,
        "clone",
        "--depth",
        "1",
        url,
        "--branch",
        branch,
        fetch_path
    ]

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
                               bufsize=10240,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]


def cleanupAction(id, options=None):
    fetch_path = os.path.join(build_location, id, "sources")
    try:
        shutil.rmtree(fetch_path)
    except:
        return False
    else:
        return True


def getMeta(id, options, meta):

    fetch_path = os.path.join(build_location, id, "sources")

    cmd = [
        gitpath,
        "rev-parse",
        "HEAD"
    ]

    process = subprocess.Popen(cmd,
                               bufsize=1024,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=fetch_path)

    commit_id, err = process.communicate()

    data = {"commit_id": commit_id.decode()[:-1]}

    return data
