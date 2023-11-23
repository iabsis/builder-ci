#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Redhat/Centos repository thanks to createrepo.
"""

import subprocess
import os
import lib.logs as logs
import glob
import shutil


process = subprocess.Popen(["which", "createrepo"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if not stdout:
    print("ERROR: createrepo is not installed")
    quit()
else:
    createrepo = stdout.splitlines()[0]


class Step:

    def runAction(self):

        base_target = os.path.join(
            self.options["default_target"], self.meta["name"], "redhat")

        try:
            os.makedirs(base_target)
        except FileExistsError:
            logs.debug("Target folder already exists")
            pass

        for file in glob.glob(self.binary_path + "/*.rpm"):
            logs.debug("Moving file: " + file)
            shutil.move(file, base_target)

        cmd = [
            createrepo,
            "-q",
            "."
        ]

        logs.debug("Command passed: " + str(cmd))

        process = subprocess.Popen(cmd,
                                   bufsize=10240,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=base_target)

        log_out, log_err = process.communicate()

        if not process.returncode == 0:
            return [False, log_out, log_err]
        else:
            return [True, log_out, log_err]

    def detect(self):
        rpm = glob.glob(os.path.join(self.binary_path, "*.rpm"))

        if not rpm == []:
            return True
