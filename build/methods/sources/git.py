#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get source files from git
"""

import subprocess
import os
import shutil
from ...step import StepAbstract

class Step(StepAbstract):

    name = "git"
    command = "git"

    def __init__(self, build, options):
        super().__init__(build, options)
        self.branch = options.get("branch") if options.get("branch") else 'master'
        self.url = self.options["url"]

    def run(self):
        
        self._run_command(
            [
                self._which(self.command),
                "clone",
                "--depth",
                "1",
                self.url,
                "--branch",
                self.branch,
                self.sources_path
            ]
        )

    @property
    def meta(self):

        self._run_command([
            self._which(self.command),
            "rev-parse",
            "HEAD"
        ])

        self.meta['commit_id'] = self.log_out.decode()[:-1]
