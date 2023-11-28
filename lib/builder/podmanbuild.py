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

    name = "podmanbuild"

    def runAction(self):

        with PodmanClient() as client:

            returncode = 0
            try:
                image, log_out_raw = client.images.build(
                    path=self.sources_path,
                    tag=self.options["tag"] if self.options[
                        "tag"] else f"builder_{self.id}",
                    dockerfile=self.options["dockerfile"] if self.options["dockerfile"] else "Dockerfile",
                    forcerm=True,
                    pull=True,
                    rm=True
                )
            except Exception as e:
                self.log_err = f"Error with image build: {e}"
                returncode = 1

            self.meta["image_id"] = image.id
            logs.debug(f"Built image id: {image.id}")

            self.log_out = ""
            for line in log_out_raw:
                l = line.decode()
                if 'stream' in l:
                    self.log_out += json.loads(l)['stream']

            if not returncode == 0:
                return [False, None, self.log_err]
            else:
                return [True, self.log_out, None]

    def detect(self):
        dockerfile = os.path.join(self.sources_path, "Dockerfile")

        if os.path.exists(dockerfile):
            return True
