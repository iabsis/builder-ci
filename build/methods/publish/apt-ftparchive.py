#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Debian/Ubuntu repository
"""

import os
import lib.logs as logs
import glob
import shutil

from ...step import StepAbstract
from pkg_resources import parse_version


class Step(StepAbstract):

    name = "apt-ftparchive"
    command = "apt-ftparchive"

    @property
    def base_target(self):
        dist = self.meta["dist"]
        arch = self.meta["arch"]

        debian_root = os.path.join(
            self.options["default_target"], self.meta["name"], "debian")
        sub_repository = os.path.join("dists", dist, "main", "binary-" + arch)
        return os.path.join(debian_root, sub_repository)

    def run(self):

        try:
            os.makedirs(self.base_target)
        except FileExistsError:
            logs.debug("Target folder already exists")
            pass

        for file in glob.glob(self.binary_path + "/*.deb"):
            logs.debug("Moving file: " + file)
            try:
                shutil.move(file, self.base_target)
            except Exception as e:
                if self.options["ignore-existing"]:
                    continue
                else:
                    raise Exception(f"Error while moving file: {e}")

        self.refreshRepo()

    def refreshRepo(self):
        opts = f'-o APT::FTPArchive::Release::Architectures="{self.arch}" -o APT::FTPArchive::Release::Codename="{self.dist}"'
        cmd = f'{self.command_path} {opts} packages dists/{self.dist} > {self.sub_repository}/Packages ; {self.command_path} release dists/{self.dist} > {self.sub_repository}/Release'

        self._runCommand(cmd, cwd=self.debian_root)

    def detect(self):

        # Define paths
        debian_deb = glob.glob(self.binary_path + "/*.deb")

        if debian_deb:
            return True

    def _sort_versions(self, versions):
        versions_objects = [parse_version(v) for v in versions]
        sorted_versions_objects = sorted(versions_objects, key=lambda x: x)
        return [str(v) for v in sorted_versions_objects]

    def cleanupAction(self):

        if not self.options['only_keep_version']:
            return True

        only_keep = self.options['only_keep_version']

        packages = {}
        for folder, path, files in os.walk(self.base_target):
            for file in files:
                if "deb" in file:
                    package_name = file.split("_")[0]
                    version = file.split("_")[1]

                    metadata = {
                        "filename": file,
                        "package_name": package_name,
                        "folder": folder
                    }
                    try:
                        packages[version].append(metadata)
                    except KeyError:
                        packages[version] = [metadata]

        versions = self._sort_versions(x for x, y in packages.items())

        print(packages)
        print(versions)

        self.log_out = ''

        for version in versions[:-only_keep]:
            for files in packages[version]:
                self.log_out += f"Deleting old file: {os.path.join(files['folder'],files['filename'])}\n"
                os.remove(
                    os.path.join(
                        files['folder'],
                        files['filename']
                    ))
