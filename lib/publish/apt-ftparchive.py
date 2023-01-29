#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Debian/Ubuntu repository
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
    "bin": "apt-ftparchive",
    "name": "apt-ftparchive",
    "meta": []
}

process = subprocess.Popen(["which", method["bin"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    print("ERROR: " + method["bin"] + " is not installed")
    quit()
else:
    bin_path = stdout.splitlines()[0].decode()

def runAction(id, options, meta):

    dist = meta["dist"]
    arch = meta["arch"]
    
    project_path = os.path.join(build_location, id)
    sources_path = os.path.join(pwd, build_location, id, "sources")
    binary_path = os.path.join(build_location, id, "binary")

    repo_path = os.path.join(options["default_target"], meta["name"])
    debian_root = os.path.join(options["default_target"], meta["name"], "debian")
    sub_repository = os.path.join("dists", dist, "main", "binary-" + arch)
    base_target = os.path.join(debian_root, sub_repository)
    
    try:
        os.makedirs(base_target)
    except FileExistsError:
        logs.debug("Target folder already exists")
        pass

    for file in glob.glob(binary_path + "/*.deb"):
        logs.debug("Moving file: " + file)
        try:
            shutil.move(file, base_target)
        except Exception as e:
            if options["ignore-existing"] == "True":
                continue
            else:
                raise Exception(f"Error while moving file: {e}")


    opts = f'-o APT::FTPArchive::Release::Architectures="{arch}" -o APT::FTPArchive::Release::Codename="{dist}"'

    cmd = f'{bin_path} {opts} packages dists/{dist} > {sub_repository}/Packages ; {bin_path} release dists/{dist} > {sub_repository}/Release'

    logs.debug("Command passed: " + str(cmd))

    process = subprocess.Popen(cmd,
        bufsize=10240,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=debian_root)
    
    process.wait()

    log_out, log_err = process.communicate()

    if not process.returncode == 0:
        return [False, log_out, log_err]
    else:
        return [True, log_out, log_err]

def getMeta(id, options, meta):
    return None

def detect(id, options, meta):
    binary_path = os.path.join(build_location, id, "binary")

    ## Define paths
    debian_deb = glob.glob(binary_path + "/*.deb")

    if debian_deb:
        return True