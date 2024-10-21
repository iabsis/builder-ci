#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module permits to publish a markdown file into wiki.
"""


import requests
import os
import lib.logs as logs
from lib.config import Config
from slugify import slugify

from ...step import StepAbstract

redmine_config = Config("redmine")


class Step(StepAbstract):

    name = "redwiki"
    mandatory_options = [
        {
            "name": "file",
            "description": "The file to upload into redmine files"
        },
        {
            "name": "page_name",
            "description": "The target page name to send the wiki page"
        }
    ]

    def run(self):

        fullpath_filename = os.path.join(
            self.binary_path, self.options["file"])
        with open(fullpath_filename, 'r') as f:
            file_content = f.read()

        headers = {
            'Content-Type': 'application/octet-stream',
            'X-Redmine-Api-Key': self.options["key"]
        }

        logs.debug(f"Publishing file: {self.options['file']} to Redmine wiki")

        if self.options["override_name"]:
            name = self.options["override_name"]
        else:
            name = self.meta["name"]

        page_slug = slugify(self.options["page_name"])

        if not self.options["url"]:
            url = redmine_config["url"] + "/projects/" + \
                name + "/wiki/" + page_slug + ".json"
        else:
            url = self.options["url"] + "/projects/" + \
                name + "/wiki/" + page_slug + ".json"

        content = {
            "wiki_page": {
                "title": self.options["page_name"],
                "text": file_content
            }
        }

        response = requests.put(url, headers=headers, json=content)

        if not response.status_code == 200:
            raise Exception(
                f"Error with redmine, got {response.status_code}, message: {response.text}")
