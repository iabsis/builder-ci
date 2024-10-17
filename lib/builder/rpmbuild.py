#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Redhat/Centos package (not advised for binary build, prefer docker otherwise)
"""

import subprocess
import os
import re
import lib.logs as logs
from lib.step import Step


class BuildStep(Step):

    name = "rpmbuild"
    command = "rpmbuild"

    def runAction(self):

        redhat_specs = os.path.join(self.build_path, "redhat",
                                    self.meta["name"] + ".spec")

        cmd = self.command_path.decode() + " -bb " + redhat_specs + \
            " --define \"_sourcedir $PWD\""

        self._runCommand(cmd, cwd=self.build_path)

    def getMeta(self):

        redhat_specs = os.path.join(
            self.build_path, "redhat", self.meta["name"] + ".spec")
        with open(redhat_specs) as f:
            for line in f.readlines():
                if "Version:" in line:
                    ver = re.split(r'[\ \:\n]', line)[2]
                elif "Release" in line:
                    release = re.split(r'[\ \:\n]', line)[2]

        self.meta["version"] = ver + "-" + release

    def detect(self):
        redhat_specs = os.path.join(
            self.sources_path, "redhat", self.meta["name"] + ".spec")

        if os.path.exists(redhat_specs):
            return True
