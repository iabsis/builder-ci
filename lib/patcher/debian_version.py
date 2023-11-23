#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import errno
import subprocess
import os
import re
from lib.config import Config
import lib.logs as logs

from lib.step import Step


process = subprocess.Popen(["which", "dch"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

stdout, stderr = process.communicate()

if not stdout:
    logs.error("ERROR: dch is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "dch")
else:
    cmdpath = stdout.splitlines()[0]


class BuildStep(Step):

    name = "debian_version"

    def runAction(self):

        cmd = [
            cmdpath,
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

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            return [True, log_out, log_err]

    def getMeta(self):

        if self.meta["old_version"]:
            return None
        with open(self.sources_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        version = f[2]
        dist = f[4]
        return {"dist": dist, "old_version": version}
