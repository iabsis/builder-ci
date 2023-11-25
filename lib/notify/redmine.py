#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Send build notification to Redmine by using Redmine Builder CI plugin.
"""

import requests
import lib.logs as logs

from lib.step import Step


class BuildStep(Step):

    def runAction(self):

        headers = {
            'Content-Type': 'application/json',
            'X-Redmine-Api-Key': self.options["key"]
        }

        json = {
            "project": self.meta["name"],
            "status": self.meta["status"].capitalize(),
            "release": self.meta["version"],
            "commit": self.meta["commit_id"],
            "target": self.meta["dist"],
            "builder": self.meta["builder"]
        }

        try:
            started_at = self.meta["start_time"].strftime("%Y-%m-%d_%H:%M:%S")
            json["started_at"] = started_at
        except:
            pass

        try:
            finished_at = self.meta["end_time"].strftime("%Y-%m-%d_%H:%M:%S")
            json["finished_at"] = finished_at
        except:
            pass

        try:
            log = logs.get_logs(id, mode="html")
            json["logs"] = log
        except:
            pass

        # Disable because it takes too much space in logs
        # logs.debug("Json content:" + str(json))

        if not self.meta["redmine_id"]:
            url = self.options["url"] + "/builds/new.json"
        else:
            url = self.options["url"] + "/builds/" + \
                self.meta["redmine_id"] + ".json"

        response = requests.post(url, headers=headers, json=json)

        if not response.status_code == 200:
            err = response.text
            if err == "":
                err = "API returned error code:" + str(response.status_code)
            log = "API returned error code:" + str(response.status_code)
            return [False, None, err]
        else:
            self.meta["redmine_id"] = response.content.decode()
            out = response.content
            return [True, out, None]
