#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Publish any files into a folder on your build server
"""

import os

from lib.config import Config
from lib.step import Step
import lib.logs as logs
import glob
import shutil
import traceback


class BuildStep(Step):

    name = "local-folder"


def runAction(self):

    source_files = self.options["source_files"]
    target_path = self.options["target_path"]
    base_target = os.path.join(
        self.options["default_target"], self.meta["name"], target_path)

    os.makedirs(base_target, exist_ok=True)

    logs.debug(self.binary_path + "/" + source_files)

    for file in glob.glob(self.binary_path + "/" + source_files):
        logs.debug("Moving file: " + file)
        shutil.move(file, base_target)
