#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Put this file into /<gitolite-path>/local/hooks/common/post-receive.d

import os
import requests

repository = os.getenv("GL_REPO")
if not repository:
    print("Error, GL_REPO is not defined, you have to run this script inside gitolite ")

builder_url = "https://contious-int:5000/build"
project = repository.split("/")[0]
git_url = "https://redmine-staging.oniabsis.com"
git_project = git_url + "/" + repository + ".git"


json = {
    "project": project,
	"sources": {
		"method": "git",
		"options": {
			"url": git_project
		}
	},
	"notify": {
		"method": "redmine"
	}
}

response = requests.post(builder_url, json=json)
if not response.status_code == 200:
    err = response.text
    if err == "":
        err = "An error has occured while notifing builder:" + str(response.status_code)
    print(err)
else:
    print("Builder notified successfully")