#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from time import sleep
import threading

from lib.config import Config
import lib.worker as worker
import lib.logs as logs

config = Config("default")

mongo_uri = config["mongo_uri"]
mongo = MongoClient(mongo_uri)
db = mongo.builder

max_threads = int(config["max_threads"]) if config["max_threads"] else 1


class runThread:

    projects_on_build = []

    def run_thread(self, id, name):

        while name in self.projects_on_build:
            logs.debug(
                f"Project with name {name} already in queue, waiting 1 second")
            sleep(1)

        while len(self.projects_on_build) > max_threads:
            logs.debug(
                f"Max threads reached {len(self.projects_on_build)} (max {max_threads}), waiting 1 second")
            sleep(1)

        self.projects_on_build.append(name)
        worker.start_build(str(id))
        self.projects_on_build.remove(name)


t = runThread()

change_stream = mongo.builder.build.watch()
for change in change_stream:

    if change["operationType"] == "insert":

        id = change["fullDocument"]["_id"]
        name = change["fullDocument"]["project"]

        logs.info(f"## Queuing {str(id)}")
        threading.Thread(target=t.run_thread, args=[
                         str(id), name]).start()
