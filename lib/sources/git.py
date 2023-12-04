#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get source files from git
"""

import subprocess
import os

from lib.config import Config
import shutil
import lib.logs as logs

from lib.step import Step


class BuildStep(Step):

    name = "git"
    command = "git"

    def runAction(self):
        url = self.options["url"]
        branch = self.options["branch"]

        cmd = [
            self.command_path,
            "clone",
            "--depth",
            "1",
            url,
            "--branch",
            branch,
            self.sources_path
        ]

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   bufsize=10240,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        self.log_out, self.log_err = process.communicate()

        if not process.returncode == 0:
            return [False, self.log_out, self.log_err]
        else:
            return [True, self.log_out, self.log_err]

    def getMeta(self):

        cmd = [
            self.command_path,
            "rev-parse",
            "HEAD"
        ]

        self._runCommand(cmd, cwd=self.sources_path)
        self.meta['commit_id'] = self.log_out.decode()[:-1]
