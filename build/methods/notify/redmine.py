#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Send build notification to Redmine by using Redmine Builder CI plugin.
"""

import requests
import lib.logs as logs

from ...step import StepAbstract


class Step(StepAbstract):

    def run(self):

        headers = {
            'Content-Type': 'application/json',
            'X-Redmine-Api-Key': self.options["key"]
        }

        json = {
            "project": self.build.meta["name"],
            "status": self.build.meta["status"].capitalize(),
            "release": self.build.meta["version"],
            "commit": self.build.meta["commit_id"],
            "target": self.build.meta["dist"],
            "builder": self.build.meta["builder"]
        }

        try:
            started_at = self.build.meta["start_time"].strftime("%Y-%m-%d_%H:%M:%S")
            json["started_at"] = started_at
        except:
            pass

        try:
            finished_at = self.build.meta["end_time"].strftime("%Y-%m-%d_%H:%M:%S")
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

        if not self.build.meta["redmine_id"]:
            url = self.options["url"] + "/builds/new.json"
        else:
            url = self.options["url"] + "/builds/" + \
                self.build.meta["redmine_id"] + ".json"

        response = requests.post(url, headers=headers, json=json)

        if not response.status_code == 200:
            raise Exception(
                f"Error with redmine, got {response.status_code}, message: {response.text}")

        self.build.meta["redmine_id"] = response.content.decode()
