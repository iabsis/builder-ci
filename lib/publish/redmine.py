#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module permits to publish any file to Redmine files project.
"""

import requests
import os
import json
import lib.logs as logs

from lib.step import Step


class BuildStep(Step):

    name = "redmine"

    def runAction(self):

        file = self.options["file"]

        if not file:
            msg = "Error, you have to define file option"
            logs.error(msg)
            return [False, None, msg]

        headers = {
            'Content-Type': 'application/octet-stream',
            'X-Redmine-Api-Key': self.options["key"]
        }

        logs.debug("Publishing file: " + file + " to Redmine")

        rootname = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        filename = rootname + "_" + self.meta["version"] + extension
        fullpath_filename = os.path.join(self.binary_path, file)
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

            file_response = requests.post(url, headers=headers, json=file_json)

            if not file_response.status_code == 200:
                err = "API returned error code:" + str(file_response.text)
                logs.error(err)
                return [False, None, err]
        return [True, None, None]
