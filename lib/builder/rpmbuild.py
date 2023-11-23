#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Redhat/Centos package (not advised for binary build, prefer docker otherwise)
"""

import subprocess
import os
import tarfile
import io
import re
from lib.config import Config
import logs
import errno
from shlex import quote

default_config = Config("default")

build_location = default_config["build_location"]

name = "rpmbuild"

process = subprocess.Popen(["which", "rpmbuild"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    logs.error("ERROR: rpmbuild is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "rpmbuild")
else:
    builderpath = stdout.splitlines()[0]


def runAction(id, options, meta):

    pwd = os.getcwd()
    build_root = os.path.join(build_location + id, "buildroot")
    spec = os.path.join("redhat", meta["name"] + ".spec")
    build_path = os.path.join(pwd, build_location + id, "sources")
    sourcedir = quote("_sourcedir " + build_path)

    cmd = builderpath.decode() + " -bb " + spec + " --define \"_sourcedir $PWD\""

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True,
                               cwd=build_path)

    process.wait()

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]


def getMeta(id, options, meta):

    build_path = os.path.join(build_location + id, "sources")
    spec = os.path.join(build_path, "redhat", meta["name"] + ".spec")
    with open(spec) as f:
        for line in f.readlines():
            if "Version:" in line:
                ver = re.split(r'[\ \:\n]', line)[2]
            elif "Release" in line:
                release = re.split(r'[\ \:\n]', line)[2]

    try:
        version = ver + "-" + release
    except:
        return None

    meta = {"version": version}
    return meta


def detect(id, options, meta):
    build_path = os.path.join(build_location, id, "sources")
    redhat_specs = os.path.join(build_path, "redhat", meta["name"] + ".spec")

    if os.path.exists(redhat_specs):
        return True
