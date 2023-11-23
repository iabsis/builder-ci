#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from podman import PodmanClient
import os
import json
import lib.logs as logs

from lib.step import Step


class BuildStep(Step):

    name = "podman"
    command = "podman"

    def runAction(self):

        with PodmanClient() as client:

            if not self.options["image"]:
                log_err = "Error, image must be defined"
                return [False, False, log_err]

            volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

            returncode = 0
            try:
                log_out = client.containers.run(
                    image=self.options["image"], volumes=volume, remove=True, environment=self.options["env"], stderr=True)
            except Exception as e:
                logs.warning(f"An error as occured with podman: {e}")
                log_err = "Error with image: " + self.options["image"]
                returncode = 1

            if not returncode == 0:
                return [False, None, log_err]
            else:
                return [True, log_out, log_out]

    def getMeta(self):

        if not self.options["image"]:
            log_err = "Error, image must be defined"
            return [False, None, log_err]

        with PodmanClient() as client:

            volume = {self.build_path: {'bind': '/build', 'mode': 'rw'}}

            print(self.build_path)

            try:
                log_out = client.containers.run(
                    image=self.options["image"], command="meta", volumes=volume, remove=True, environment=self.options["env"])
            except Exception as e:
                logs.warning(f"An error as occured with podman: {e}")
                returncode = 1
                log_err = "Container image not found" + self.options["image"]

            data = log_out.decode()
            return json.loads(data)

    def detect(self):

        if not self.command_path:
            return False

        docker_file = os.path.join(self.sources_path, "Dockerfile")

        if os.path.exists(docker_file):
            return True
