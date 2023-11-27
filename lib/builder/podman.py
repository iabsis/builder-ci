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
    mandatory_options = [
        {
            "name": "image",
            "description": "The image name to build"
        }
    ]

    def runAction(self):

        with PodmanClient() as client:

            mounts = [{
                "target": "/build",
                "read_only": False,
                "source": self.build_path,
                "type": "bind"
            }]

            returncode = 0
            try:
                log_out = client.containers.run(
                    image=self.options["image"], mounts=mounts, remove=True, environment=self.options["env"], stderr=True)
            except Exception as e:
                logs.warning(f"An error as occured with podman: {e}")
                log_err = "Error with image: " + self.options["image"]
                returncode = 1

            if not returncode == 0:
                return [False, None, log_err]
            else:
                return [True, log_out, log_out]
