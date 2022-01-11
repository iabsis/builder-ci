#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import io
import re
import config
import logs
import glob
import shutil

name = "debian_version"

build_location = config.getSection("default")["build_location"]

pwd = os.getcwd()

process = subprocess.Popen(["which", "dch"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    logs.error("ERROR: dch is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "dch") 
else:
    cmdpath = stdout.splitlines()[0]

def runAction(id, options, meta):
    
    sources_path = os.path.join(pwd, build_location, id, "sources")
    
    logs.debug(sources_path)
    
    cmd = [
        cmdpath,
        "-v",
        options["version"],
        "--distribution",
        meta["dist"],
        "New upstream release"
    ]
    
    logs.debug("Command passed: " + str(cmd))
    
    process = subprocess.Popen(cmd,
        bufsize=1024,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=sources_path)

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]

def cleanupAction(id, options=None):
    pass
    
def getMeta(id, options, meta):

    build_path = os.path.join(build_location + id, "sources")
    with open(build_path + "/debian/changelog", "r") as f:
        firstline = f.readline()
    f = re.split(r'[()\ \;]', firstline)
    version = f[2]
    dist = f[4]
    return {"dist": dist, "old_version": version}