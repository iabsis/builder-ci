#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

name = "docker"

def runAction(id, options, meta):

    pwd = os.getcwd()
    build_path = os.path.join(pwd, build_location + id)

    if not options["image"]:
        log_err = "Error, image must be defined"
        return [False, False, log_err]

    client = docker.from_env()
    volume = {build_path: {'bind': '/build', 'mode': 'rw'}}
    
    returncode = 0
    try:
        log_out = client.containers.run(image=options["image"], volumes=volume, remove=True, environment=options["env"])
    except:
        log_err = "Error with image: " + options["image"]
        returncode = 1
    
    if not returncode == 0:
        return [False, None, log_err]
    else:
        return [True, log_out, log_out]

def getMeta(id, options, meta):

    pwd = os.getcwd()
    build_path = os.path.join(pwd, build_location + id)

    if not options["image"]:
        log_err = "Error, image must be defined"
        return [False, None, log_err]

    client = docker.from_env()
    volume = {build_path: {'bind': '/build', 'mode': 'rw'}}
    
    returncode = 0
    try:
        log_out = client.containers.run(image=options["image"], command="meta", volumes=volume, remove=True, environment=options["env"])
    except:
        returncode = 1
        log_err = "Container image not found" + options["image"]
    
    meta = log_out.decode()
    return json.loads(meta)


def detect(id, options, meta):
    return False
