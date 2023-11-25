#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

import docker
import os
import config
import json
from shlex import quote


from lib.step import Step


class BuildStep(Step):

    name = "dockerbuild"
    mandatory_options = [
        {
            "name": "tag",
            "description": "The target tag to build"
        }
    ]

    def runAction(self):

        client = docker.from_env()

        # Build the image
        returncode = 0
        try:
            log_out = client.images.build(
                '.', tag=self.options["tag"], rm=True, pull=True, forcerm=True)
        except:
            log_err = "Error with image: " + self.options["image"]
            returncode = 1

        if not returncode == 0:
            return [False, None, log_err]
        else:
            return [True, log_out, log_out]

    def getMeta(self):

        pwd = os.getcwd()

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        returncode = 0
        try:
            log_out = client.containers.run(
                image=self.options["image"], command="meta", volumes=volume, remove=True, environment=self.options["env"])
        except:
            returncode = 1
            log_err = "Container image not found" + self.options["image"]

        data = log_out.decode()
        return json.loads(data)
