#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import errno
import subprocess
import os
import re
from lib.config import Config
import lib.logs as logs

from ...step import StepAbstract


class Step(StepAbstract):

    name = "debian_version"
    command = "dch"

    def run(self):

        cmd = [
            self.command_path,
            "--force-distribution",
            "-v",
            self.options["version"],
            "--distribution",
            self.meta["dist"],
            "New upstream release"
        ]

        self._runCommand(cmd, cwd=self.sources_path)

        logs.debug("Command passed: " + str(cmd))

    def meta(self):

        if self.build.meta["old_version"]:
            return None
        with open(self.sources_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        self.build.meta['old_version'] = f[2]
        self.build.meta['dist'] = f[4]
