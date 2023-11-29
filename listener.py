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

max_threads = config["max_threads"] if config["max_threads"] else 1
# It seems required to check current thread, probably mongo already use some
current_threads = threading.active_count()

change_stream = mongo.builder.build.watch()
for change in change_stream:

    if change["operationType"] == "insert":

        id = change["fullDocument"]["_id"]

        while threading.active_count() > max_threads + current_threads:
            logs.debug(
                f"Max threads reached, waiting 1 second: {threading.active_count() - current_threads}")
            sleep(1)

        logs.info(f"## Queuing {str(id)}")
        t = threading.Thread(target=worker.start_build, args=[str(id)])
        t.start()
