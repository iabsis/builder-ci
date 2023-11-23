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

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True,
                                   cwd=self.build_path)

        process.wait()

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            return [True, log_out, log_err]

    def getMeta(self):

        redhat_specs = os.path.join(
            self.build_path, "redhat", meta["name"] + ".spec")
        with open(redhat_specs) as f:
            for line in f.readlines():
                if "Version:" in line:
                    ver = re.split(r'[\ \:\n]', line)[2]
                elif "Release" in line:
                    release = re.split(r'[\ \:\n]', line)[2]

        try:
            version = ver + "-" + release
        except:
            return None

        meta = {"version": version}
        return meta

    def detect(self):
        redhat_specs = os.path.join(
            self.sources_path, "redhat", self.meta["name"] + ".spec")

        if os.path.exists(redhat_specs):
            return True
