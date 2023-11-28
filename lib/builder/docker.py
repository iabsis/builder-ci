#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

import docker
import os
import json

from lib.step import Step


class BuildStep(Step):

    name = "docker"
    command = "docker"

    def runAction(self):

        if not self.options["image"]:
            self.log_err = "Error, image must be defined"
            return [False, False, self.log_err]

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        returncode = 0
        try:
            self.log_out = client.containers.run(
                image=self.options["image"], volumes=volume, remove=True, environment=self.options["env"], stderr=True)
        except:
            self.log_err = "Error with image: " + self.options["image"]
            returncode = 1

        if not returncode == 0:
            return [False, None, self.log_err]
        else:
            return [True, self.log_out, self.log_out]

    def getMeta(self):

        if not self.options["image"]:
            log_err = "Error, image must be defined"
            return [False, None, log_err]

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        returncode = 0
        try:
            self.log_out = client.containers.run(
                image=self.options["image"], command="meta", volumes=volume, remove=True, environment=self.options["env"])
        except:
            returncode = 1
            log_err = "Container image not found" + self.options["image"]

        data = self.log_out.decode()
        return json.loads(data)
