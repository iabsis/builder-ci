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
    mandatory_options = [
        {
            "name": "image",
            "description": "The image name to build"
        }
    ]

    def runAction(self):

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        self.log_out = client.containers.run(
            image=self.options["image"], volumes=volume, remove=True, environment=self.options["env"], stderr=True)

    def getMeta(self):

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        self.log_out = client.containers.run(
            image=self.options["image"], command="meta", volumes=volume, remove=True, environment=self.options["env"])

        data = json.loads(self.log_out.decode())
        for key, value in data:
            self.meta[key] = value
