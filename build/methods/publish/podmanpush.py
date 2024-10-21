#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from ...step import StepAbstract
from podman import PodmanClient
from lib.config import Config
import json

config = Config("docker")


class Step(StepAbstract):

    name = "podmanpush"
    mandatory_options = [
        {
            "name": "destination",
            "description": "The tag destination where to send the image"
        }
    ]

    def run(self):

        with PodmanClient() as client:

            # Which tag must be used?
            tag = self.options["tag"] if self.options[
                "tag"] else f"builder_{self.id}"

            auth_config = {
                "username": config["username"],
                "password": config["password"]
            }

            self.log_out = client.images.push(
                repository=tag,
                destination=self.options["destination"],
                auth_config=auth_config
            )

            if not self.options["keep_image"]:
                self.log_out = client.images.remove(image=tag)

            if not self.options["no_prune"]:
                client.images.prune()
