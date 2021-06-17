#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import tarfile
import io
import re
import config
import logs
import glob
import shutil

build_location = config.getSection("default")["build_location"]
pwd = os.getcwd()

name = "pbuilder"

process = subprocess.Popen(["which", "pdebuild"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

file_to_move = ["*.deb", "*.dsc", "*.changes", "*.xz", "*.tar.gz", "*.tar.bz2"]

if not stdout:
    logs.error("ERROR: pbuilder is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "pdebuild") 
else:
    pbuilderpath = stdout.splitlines()[0]

def runAction(id, options, meta):

    project_path = os.path.join(build_location, id)
    sources_path = os.path.join(pwd, build_location, id, "sources")
    binary_path = os.path.join(build_location, id, "binary")

    processor = options["processor"]
    if not processor:
        error = "processor is not defined into options"
        logs.error(error)
        return [False, None, error]
        
    dist = options["dist"]
    if not dist:
        error = "dist is not defined into options"
        logs.error(error)
        return [False, None, error]

    basetgz = options["basetgz"] + dist + "-" + processor + ".tgz"

    cmd = [  
        pbuilderpath,
        "--use-pdebuild-internal",
        "--",
        "--hookdir",
        "debian/hooks/",
        "--basetgz",
        basetgz
    ]

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
        bufsize=10240,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=sources_path)

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        try:
            os.makedirs(binary_path);
        except FileExistsError:
            pass
        for wildcard in file_to_move:
            for file in glob.glob(project_path + "/" + wildcard):
                logs.debug("#File:" + file)
                shutil.move(file, binary_path)

        return [True, log_out, log_err]


def getMeta(id, options, meta):

    build_path = os.path.join(build_location + id, "sources")
    with open(build_path + "/debian/changelog", "r") as f:
        firstline = f.readline()
    f = re.split(r'[()\ \;]', firstline)
    version = f[2]
    dist = f[4]
    arch = options["processor"]
    meta = {"dist": dist, "version": version, "arch": arch}
    return meta


def detect(id, options, meta):
    build_path = os.path.join(build_location, id, "sources")
    debian_changelog = os.path.join(build_path, "debian/changelog")

    if os.path.exists(debian_changelog):
        return True