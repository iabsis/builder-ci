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
    mandatory_options = [
        {
            "name": "destination",
            "description": "The tag destination where to send the image"
        }
    ]

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
        tag = self.options["tag"] if self.options[
            "tag"] else f"builder_{self.id}"

        returncode = 0
        try:
            log_out = client.images.push(
                tag=tag, destination=self.options["destination"])
        except:
            log_err = "Error pushing image: " + self.options["image"]
            returncode = 1

        if not keep_image:
            log_out += client.images.remove(tag=self.options["tag"])

        if not returncode == 0:
            return [False, None, log_err]
        else:
            return [True, log_out, log_out]
