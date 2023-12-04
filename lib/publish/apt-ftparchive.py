#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Debian/Ubuntu repository
"""

import subprocess
import os
from lib.config import Config
import lib.logs as logs
import glob
import shutil

from lib.step import Step


class BuildStep(Step):

    name = "apt-ftparchive"
    command = "apt-ftparchive"
    mandatory_options = [
        {
            "name": "image",
            "description": "The image name to build"
        }
    ]

    def runAction(self):

        dist = self.meta["dist"]
        arch = self.meta["arch"]

        debian_root = os.path.join(
            self.options["default_target"], self.meta["name"], "debian")
        sub_repository = os.path.join("dists", dist, "main", "binary-" + arch)
        base_target = os.path.join(debian_root, sub_repository)

        try:
            os.makedirs(base_target)
        except FileExistsError:
            logs.debug("Target folder already exists")
            pass

        for file in glob.glob(self.binary_path + "/*.deb"):
            logs.debug("Moving file: " + file)
            try:
                shutil.move(file, base_target)
            except Exception as e:
                if self.options["ignore-existing"]:
                    continue
                else:
                    raise Exception(f"Error while moving file: {e}")

        opts = f'-o APT::FTPArchive::Release::Architectures="{arch}" -o APT::FTPArchive::Release::Codename="{dist}"'
        cmd = f'{self.command_path} {opts} packages dists/{dist} > {sub_repository}/Packages ; {self.command_path} release dists/{dist} > {sub_repository}/Release'

        self._runCommand(cmd, cwd=debian_root)

    def detect(self):

        # Define paths
        debian_deb = glob.glob(self.binary_path + "/*.deb")

        if debian_deb:
            return True
