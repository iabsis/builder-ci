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

        cmd = f'{self.command_path} {opts} packages dists/{dist} > {sub_repository}/Packages ; {bin_path} release dists/{dist} > {sub_repository}/Release'

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   bufsize=10240,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True,
                                   cwd=debian_root)

        process.wait()

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            return [True, log_out, log_err]

    def detect(self):

        # Define paths
        debian_deb = glob.glob(self.binary_path + "/*.deb")

        if debian_deb:
            return True
