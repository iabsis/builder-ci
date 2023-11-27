#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from lib.step import Step
import docker
import os
from lib.config import Config
import json

config = Config("docker")


class BuildStep(Step):

    name = "dockerpush"

    def runAction(self):

        # Check for mandatory info
        if not self.options["tag"]:
            log_err = "Error, tag must be defined"
            return [False, False, log_err]

        # Check for mandatory info
        # Check if we keep image
        keep_image = self.options["keep_image"]

        client = docker.from_env()

        # Build the image
        returncode = 0
        try:
            log_out = client.images.push(tag=self.options["tag"])
        except:
            log_err = "Error pushing image: " + self.options["image"]
            returncode = 1

        if not keep_image:
            log_out += client.images.remove(tag=self.options["tag"])

        if not returncode == 0:
            return [False, None, log_err]
        else:
            return [True, log_out, log_out]

    def getMeta(self):

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
