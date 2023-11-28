#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import errno
import subprocess
import os
import re
from lib.config import Config
import lib.logs as logs

from lib.step import Step


class BuildStep(Step):

    name = "debian_version"
    command = "dch"

    def runAction(self):

        cmd = [
            self.command_path,
            "-v",
            self.options["version"],
            "--distribution",
            self.meta["dist"],
            "New upstream release"
        ]

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   bufsize=1024,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=self.sources_path)

        self.log_out, self.log_err = process.communicate()

        if not process.returncode == 0:
            return [False, self.log_out, self.log_err]
        else:
            return [True, self.log_out, self.log_err]

    def getMeta(self):

        if self.meta["old_version"]:
            return None
        with open(self.sources_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        version = f[2]
        dist = f[4]
        return {"dist": dist, "old_version": version}
