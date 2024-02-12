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
        },
        {
            "name": "tag",
            "description": "The tag destination where to send the image"
        }
    ]

    def runAction(self):

        # Check for mandatory info
        # Check if we keep image
        keep_image = self.options["keep_image"]

        client = docker.from_env()

        # Build the image
        tag = self.options["tag"] if self.options[
            "tag"] else f"builder_{self.id}"

        self.log_out = client.images.push(
            tag=tag, destination=self.options["destination"])

        if not keep_image:
            self.log_out += client.images.remove(tag=self.options["tag"])
