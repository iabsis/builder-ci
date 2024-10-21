#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Debian/Ubuntu package
"""


import subprocess
import os
import re

from ...step import StepAbstract


class Step(StepAbstract):

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

    def run(self):

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

        self._run_command(cmd)
        self._move_to_binary_folder(file_to_move=["*.deb", "*.dsc", "*.changes",
                                         "*.xz", "*.tar.gz", "*.tar.bz2"])
    @property
    def meta(self):

        with open(self.sources_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        version = f[2]
        dist = f[4]
        arch = self.options["processor"]
        self.build.meta['dist'] = dist
        self.build.meta["version"] = version
        self.build.meta["arch"] = arch
        return self.build.meta

    def detect(self):
        debian_changelog = os.path.join(self.sources_path, "debian/changelog")

        if os.path.exists(debian_changelog):
            return True
