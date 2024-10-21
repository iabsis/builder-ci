#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from podman import PodmanClient
from ...step import StepAbstract


class Step(StepAbstract):

    name = "podman"
    command = "podman"
    mandatory_options = [
        {
            "name": "image",
            "description": "The image name to build"
        }
    ]

    def __init__(self, id, options, meta) -> None:
        if options['url']:
            self.url = options['url']
        else:
            self.url = "unix:///run/podman/podman.sock"
        super().__init__(id, options, meta)

    def run(self):

        with PodmanClient(base_url=self.url) as client:

            mounts = [{
                "target": "/build",
                "read_only": False,
                "source": self.build_path,
                "type": "bind"
            }]

            self.log_out = client.containers.run(
                image=self.options["image"], mounts=mounts, remove=True, environment=self.options["env"], stderr=True)
