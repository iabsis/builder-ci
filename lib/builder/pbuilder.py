#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build native Debian/Ubuntu package
"""

import errno
import subprocess
import os
import re
import lib.logs as logs
import glob
import shutil

from lib.step import Step

process = subprocess.Popen(["which", "pdebuild"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

stdout, stderr = process.communicate()

file_to_move = ["*.deb", "*.dsc", "*.changes", "*.xz", "*.tar.gz", "*.tar.bz2"]

if not stdout:
    logs.error("ERROR: pbuilder is not installed")
    raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), "pdebuild")
else:
    pbuilderpath = stdout.splitlines()[0]


class BuildStep(Step):

    name = "pbuilder"

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
            pbuilderpath,
            "--use-pdebuild-internal",
            "--",
            "--hookdir",
            "debian/hooks/",
            "--basetgz",
            basetgz
        ]

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   bufsize=10240,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=self.sources_path)

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            try:
                os.makedirs(self.binary_path)
            except FileExistsError:
                pass
            for wildcard in file_to_move:
                for file in glob.glob(self.build_path + "/" + wildcard):
                    logs.debug("#File:" + file)
                    shutil.move(file, self.binary_path)

            return [True, log_out, log_err]

    def getMeta(self):

        with open(self.build_path + "/debian/changelog", "r") as f:
            firstline = f.readline()
        f = re.split(r'[()\ \;]', firstline)
        version = f[2]
        dist = f[4]
        arch = self.options["processor"]
        data = {"dist": dist, "version": version, "arch": arch}
        return data

    def detect(self):
        debian_changelog = os.path.join(self.build_path, "debian/changelog")

        if os.path.exists(debian_changelog):
            return True
