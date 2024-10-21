#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module permits to publish any file to Redmine files project.
"""

import requests
import os
import json
import lib.logs as logs

from ...step import StepAbstract


class Step(StepAbstract):

    name = "redmine"
    mandatory_options = [
        {
            "name": "file",
            "description": "The file to upload into redmine files"
        },
        {
            "name": "key",
            "description": "The redmine key with upload to project permission"
        }
    ]

    def run(self):

        headers = {
            'Content-Type': 'application/octet-stream',
            'X-Redmine-Api-Key': self.options["key"]
        }

        logs.debug(f"Publishing file: {self.options['file']} to Redmine")

        rootname = os.path.splitext(self.options["file"])[0]
        extension = os.path.splitext(self.options["file"])[1]
        filename = f"{rootname}_{self.meta['version']}{extension}"
        fullpath_filename = os.path.join(
            self.binary_path, self.options["file"])
        if self.options["override_name"]:
            name = self.options["override_name"]
        else:
            name = self.meta["name"]

        url = self.options["url"] + "/uploads.json?filename=" + filename
        with open(fullpath_filename, 'rb') as f:
            file_response = requests.post(url, headers=headers, data=f.read())

        if file_response.status_code == 201:
            file_id = json.loads(file_response.text)["upload"]["token"]

            headers = {
                'Content-Type': 'application/json',
                'X-Redmine-Api-Key': self.options["key"]
            }

            url = self.options["url"] + "/projects/" + \
                name + "/" + "files.json"

            file_json = {
                "file": {
                    "token": file_id
                }
            }

            response = requests.post(url, headers=headers, json=file_json)

            if not response.status_code == 200:
                raise Exception(
                    f"Error with redmine, got {response.status_code}, message: {response.text}")
