#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logs
from bson.json_util import dumps

def runAction(id, options, meta):

    headers = {
        'Content-Type': 'application/json',
        'X-Redmine-Api-Key': options["key"]
    }

    json = {
        "project": meta["name"],
        "status": meta["status"].capitalize(),
        "release": meta["version"],
        "commit": meta["commit_id"],
        "target": meta["dist"],
        "builder": meta["builder"]
    }

    try:
        started_at = meta["start_time"].strftime("%Y-%m-%d_%H:%M:%S")
        json["started_at"] = started_at
    except:
        pass

    try:
        finished_at = meta["end_time"].strftime("%Y-%m-%d_%H:%M:%S")
        json["finished_at"] = finished_at
    except:
        pass

    try:
        log = logs.get_logs(id, mode="html")
        json["logs"] = log
    except:
        pass

    #Disable because it takes too much space in logs
    #logs.debug("Json content:" + str(json))

    if not meta["redmine_id"]:
        url = options["url"] + "/builds/new.json"
    else:
        url = options["url"] + "/builds/" + meta["redmine_id"] + ".json"

    response = requests.post(url, headers=headers, json=json)

    if not response.status_code == 200:
        err = response.text
        if err == "":
            err = "API returned error code:" + str(response.status_code)
        log = "API returned error code:" + str(response.status_code)
        return [False, None, err]
    else:
        meta["redmine_id"] = response.content.decode()
        meta.saveMeta()
        out = response.content
        return [True, out, None]


def getMeta(id, options, meta):
    return None