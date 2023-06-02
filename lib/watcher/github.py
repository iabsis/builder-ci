#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def getLastVersion(id, options):

    owner = options["url"].split("/")[3]
    repo = options["url"].split("/")[4]

    if options["build_on_new"] == "release":
         
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        
        r = requests.get(url=url)
        
        for release in r.json():
            release = re.sub('[a-zA-Z_]+', '', release["tag_name"])
            return {"version": release}
