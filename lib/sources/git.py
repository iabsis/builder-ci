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

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            return [True, log_out, log_err]

    def cleanupAction(self):
        try:
            shutil.rmtree(self.sources_path)
        except:
            return False
        else:
            return True

    def getMeta(self):

        cmd = [
            self.command_path,
            "rev-parse",
            "HEAD"
        ]

        process = subprocess.Popen(cmd,
                                   bufsize=1024,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=self.sources_path)

        commit_id, err = process.communicate()

        data = {"commit_id": commit_id.decode()[:-1]}

        return data
