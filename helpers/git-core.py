#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Put this file into <git bare>/.git/hooks/post-receive

import os
import requests

repository = os.getcwd()

builder_url = "http://contious-int:5000/build"
project = repository.split("/")[-1]
git_url = "http://redmine-staging.oniabsis.com"
git_project = git_url + "/git/" + project


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