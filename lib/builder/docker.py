#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import tarfile
import io
import re
import config
import logs
import errno
import json
from shlex import quote

build_location = config.getSection("default")["build_location"]

name = "docker"

process = subprocess.Popen(["which", "docker"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    logs.error("ERROR: docker is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "docker") 
else:
    builderpath = stdout.splitlines()[0]

def runAction(id, options, meta):

    pwd = os.getcwd()
    spec = os.path.join("redhat", meta["name"] + ".spec")
    build_path = os.path.join(pwd, build_location + id)

    if not options["image"]:
        log_err = "Error, image must be defined"
        return [False, log_out, log_err]

    cmd1 = [
        builderpath,
        "run",
        "--rm"
    ]

    environment = __buildDockerEnv(options["env"])

    cmd2 = [
        "-v",
        build_path + ":/build",
        options["image"]
    ]

    cmd = cmd1 + environment + cmd2

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=build_path)

    process.wait()

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]


def getMeta(id, options, meta):

    pwd = os.getcwd()
    spec = os.path.join("redhat", meta["name"] + ".spec")
    build_path = os.path.join(pwd, build_location + id)

    if not options["image"]:
        log_err = "Error, image must be defined"
        return [False, log_out, log_err]


    cmd1 = [
        builderpath,
        "run",
        "--rm"
    ]

    environment = __buildDockerEnv(options["env"])


    cmd2 = [
        "-v",
        build_path + ":/build",
        options["image"],
        "meta"
    ]

    cmd = cmd1 + environment + cmd2

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=build_path)

    process.wait()

    log_out, log_err = process.communicate()
    
    meta = log_out.decode()
    return json.loads(meta)


def detect(id, options, meta):
    return False

def __buildDockerEnv(env):
    
    environment = []
    if env:
        for key, value in env.items():
            environment.append("-e")
            environment.append(key + "=" + value)
    
    return environment