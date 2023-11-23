#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Redhat/Centos package (not advised for binary build, prefer docker otherwise)
"""

import subprocess
import os
import re
from lib.config import Config
import lib.logs as logs
import errno
from shlex import quote

from lib.step import Step


process = subprocess.Popen(["which", "rpmbuild"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    logs.error("ERROR: rpmbuild is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "rpmbuild")
else:
    builderpath = stdout.splitlines()[0]


class BuildStep(Step):

    name = "rpmbuild"

    def runAction(self):

        pwd = os.getcwd()

        spec = os.path.join("redhat", self.meta["name"] + ".spec")

        sourcedir = quote("_sourcedir " + self.build_path)

        cmd = builderpath.decode() + " -bb " + spec + " --define \"_sourcedir $PWD\""

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

        spec = os.path.join(self.build_path, "redhat", meta["name"] + ".spec")
        with open(spec) as f:
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
            self.build_path, "redhat", self.meta["name"] + ".spec")

        if os.path.exists(redhat_specs):
            return True
