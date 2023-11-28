#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from lib.step import Step
from podman import PodmanClient
from lib.config import Config
import json

config = Config("docker")


class BuildStep(Step):

    name = "podmanpush"
    mandatory_options = [
        {
            "name": "destination",
            "description": "The tag destination where to send the image"
        },
        {
            "name": "username",
            "description": "The Docker username allowed to push image"
        },
        {
            "name": "password",
            "description": "The Docker password for user allowed to push image"
        }
    ]

    def runAction(self):

        with PodmanClient() as client:

            # Which tag must be used?
            tag = self.options["tag"] if self.options[
                "tag"] else f"builder_{self.id}"

            auth_config = {
                "username": "iabsisch",
                "password": "Vatt1ogCegMuj"
            }

            # Push the image
            returncode = 0
            try:
                log_out = client.images.push(
                    repository=tag,
                    destination=self.options["destination"],
                    auth_config=auth_config
                )
            except:
                log_err = "Error pushing image: " + self.options["destination"]
                returncode = 1

            if not self.options["keep_image"]:
                log_out += client.images.remove(image=tag)

            if not returncode == 0:
                return [False, None, log_err]
            else:
                return [True, log_out, log_out]
