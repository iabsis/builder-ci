#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

import docker
import json

from ...step import StepAbstract

class Step(StepAbstract):

    name = "dockerbuild"
    mandatory_options = [
        {
            "name": "tag",
            "description": "The target tag to build"
        }
    ]

    def run(self):

        client = docker.from_env()

        self.log_out = client.images.build(
            '.', tag=self.options["tag"], rm=True, pull=True, forcerm=True)

    @property
    def meta(self):

        client = docker.from_env()
        volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

        self.log_out = client.containers.run(
            image=self.options["image"], command="meta", volumes=volume, remove=True, environment=self.options["env"])

        data = json.loads(self.log_out.decode())
        for key, value in data:
            self.build.meta[key] = value
        return self.build.meta
