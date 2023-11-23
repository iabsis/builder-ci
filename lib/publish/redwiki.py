#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module permits to publish a markdown file into wiki.
"""


import glob
import requests
import os
import json
import logs
from lib.config import Config
from slugify import slugify

default_config = Config("default")
build_location = default_config["build_location"]

redmine_config = Config("redmine")
pwd = os.getcwd()


def runAction(id, options, meta):

    file = options["file"]

    if not file:
        msg = "Error, you have to define file option"
        logs.error(msg)
        return [False, None, msg]

    fullpath_filename = os.path.join(pwd, binary_path, file)
    with open(fullpath_filename, 'r') as f:
        file_content = f.read()

    page_name = options["page_name"]
    if not page_name:
        msg = "Error, you have to define target option"
        logs.error(msg)
        return [False, None, msg]

    headers = {
        'Content-Type': 'application/octet-stream',
        'X-Redmine-Api-Key': options["key"]
    }

    logs.debug("Publishing file: " + file + " to Redmine wiki")

    binary_path = os.path.join(build_location, id, "binary")

    if options["override_name"]:
        name = options["override_name"]
    else:
        name = meta["name"]

    page_slug = slugify(page_name)

    if not options["url"]:
        url = redmine_config["url"] + "/projects/" + \
            name + "/wiki/" + page_slug + ".json"
    else:
        url = options["url"] + "/projects/" + \
            name + "/wiki/" + page_slug + ".json"

    content = {
        "wiki_page": {
            "title": page_name,
            "text": file_content
        }
    }

    file_response = requests.put(url, headers=headers, json=content)

    if not file_response.status_code == 200:
        err = "API returned error code:" + str(file_response.text)
        logs.error(err)
        return [False, None, err]

    return [True, None, None]


def getMeta(id, options, meta):
    return None


def detect(id, options, meta):
    return False
