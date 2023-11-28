#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Debian/Ubuntu package
"""


import subprocess
import os
import re
import lib.logs as logs


from lib.step import Step


class BuildStep(Step):

    name: str = "pbuilder"
    command: subprocess = "pbuilder"

    mandatory_options = [
        {
            "name": "processor",
            "description": "Processor Arch to use for the build"
        },
        {
            "name": "dist",
            "description": "Debian/Ubuntu distribution to use"
        }
    ]

    def runAction(self):

        basetgz = f"{self.options['basetgz']}{self.options['dist']}-{self.options['processor']}.tgz"

        cmd = [
            self.command_path,
            "--use-pdebuild-internal",
            "--",
            "--hookdir",
            "debian/hooks/",
            "--basetgz",
            basetgz
        ]

        self._runCommand(cmd)
        self._moveToBinary(file_to_move=["*.deb", "*.dsc", "*.changes",
                                         "*.xz", "*.tar.gz", "*.tar.bz2"])

        return [True, self.log_out, self.log_err]

    def getMeta(self):

        with open(self.sources_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        version = f[2]
        dist = f[4]
        arch = self.options["processor"]
        data = {"dist": dist, "version": version, "arch": arch}
        return data

    def detect(self):
        debian_changelog = os.path.join(self.sources_path, "debian/changelog")

        if os.path.exists(debian_changelog):
            return True
