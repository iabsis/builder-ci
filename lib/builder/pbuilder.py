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

    def runAction(self):

        processor = self.options["processor"]
        if not processor:
            error = "processor is not defined into options"
            logs.error(error)
            return [False, None, error]

        dist = self.options["dist"]
        if not dist:
            error = "dist is not defined into options"
            logs.error(error)
            return [False, None, error]

        basetgz = self.options["basetgz"] + dist + "-" + processor + ".tgz"

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
