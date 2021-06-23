#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module permits to publish any file to Redmine files project.
"""


import glob
import requests
import os
import json
import logs
import config

build_location = config.getSection("default")["build_location"]
pwd = os.getcwd()

method = {
    "bin": "createrepo",
    "name": "createrepo",
    "meta": []
}


def runAction(id, options, meta):
    binary_path = os.path.join(build_location, id, "binary")

    file = options["file"]

    if not file:
        msg = "Error, you have to define file option"
        logs.error(msg)
        return [False, None, msg]

    headers = {
        'Content-Type': 'application/octet-stream',
        'X-Redmine-Api-Key': options["key"]
    }

    logs.debug("Publishing file: " + file + " to Redmine")

    binary_path = os.path.join(build_location, id, "binary")

    basename= os.path.basename(file)
    rootname = os.path.splitext(file)[0]
    extension = os.path.splitext(file)[1]
    filename = rootname + "_" + meta["version"] + extension
    fullpath_filename = os.path.join(pwd, binary_path, file)
    if options["override_name"]:
        name = options["override_name"]
    else:
        name = meta["name"]

    url = options["url"] + "/uploads.json?filename=" + filename
    with open(fullpath_filename, 'rb') as f:
        file_response = requests.post(url, headers=headers, data=f.read())

    if file_response.status_code == 201:
        file_id = json.loads(file_response.text)["upload"]["token"]

        headers = {
            'Content-Type': 'application/json',
            'X-Redmine-Api-Key': options["key"]
        }

        url = options["url"] + "/projects/" + name + "/" + "files.json"

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

def getMeta(id, options, meta):
    return None

def detect(id, options, meta):
    return False