#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build any kind of packages
"""

from podman import PodmanClient
import os
import json
import lib.logs as logs

from ...step import StepAbstract


class BuildStep(StepAbstract):

    name = "podmanbuild"

    def __init__(self, id, options, meta) -> None:
        if options['url']:
            self.url = options['url']
        else:
            self.url = "unix:///run/podman/podman.sock"
        super().__init__(id, options, meta)

    def run(self):

        with PodmanClient(base_url=self.url) as client:

            image, log_out_raw = client.images.build(
                path=self.sources_path,
                tag=self.options["tag"] if self.options[
                    "tag"] else f"builder_{self.id}",
                dockerfile=self.options["dockerfile"] if self.options["dockerfile"] else "Dockerfile",
                forcerm=True,
                pull=True,
                rm=True
            )

            self.meta["image_id"] = image.id
            logs.debug(f"Built image id: {image.id}")

            self.log_out = ""
            for line in log_out_raw:
                l = line.decode()
                if 'stream' in l:
                    self.log_out += json.loads(l)['stream']

    def detect(self):
        dockerfile = os.path.join(self.sources_path, "Dockerfile")

        if os.path.exists(dockerfile):
            return True
