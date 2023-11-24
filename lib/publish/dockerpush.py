#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

import docker
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

name = "dockerpush"


def runAction(id, options, meta):

    # Check for mandatory info
    if not options["tag"]:
        log_err = "Error, tag must be defined"
        return [False, False, log_err]

    # Check for mandatory info
    # Check if we keep image
    keep_image = options["keep_image"]

    client = docker.from_env()

    # Build the image
    returncode = 0
    try:
        log_out = client.images.push(tag=options["tag"])
    except:
        log_err = "Error pushing image: " + options["image"]
        returncode = 1

    if not keep_image:
        log_out += client.images.remove(tag=options["tag"])

    if not returncode == 0:
        return [False, None, log_err]
    else:
        return [True, log_out, log_out]


def getMeta(id, options, meta):

    pwd = os.getcwd()
    build_path = os.path.join(pwd, build_location + id)

    client = docker.from_env()
    volume = {build_path: {'bind': '/build', 'mode': 'rw'}}

    returncode = 0
    try:
        log_out = client.containers.run(
            image=options["image"], command="meta", volumes=volume, remove=True, environment=options["env"])
    except:
        returncode = 1
        log_err = "Container image not found" + options["image"]

    data = log_out.decode()
    return json.loads(data)


def detect(id, options, meta):
    return False
