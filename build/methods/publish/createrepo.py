#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Redhat/Centos repository thanks to createrepo.
"""

import os
from lib.step import Step
import glob

from ...step import StepAbstract
class BuildStep(StepAbstract):

    name = "createrepo"
    command = "createrepo"

    def run(self):

        base_target = os.path.join(
            self.options["default_target"], self.meta["name"], "redhat")

        self._moveToSpecific(
            glob.glob(self.binary_path + "/*.rpm"),
            base_target)

        cmd = [
            self.command_path,
            "-q",
            "."
        ]

        self._runCommand(cmd)

    def detect(self):
        rpm = glob.glob(os.path.join(self.binary_path, "*.rpm"))

        if not rpm == []:
            return True
