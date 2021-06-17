#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId

import sys
sys.path.append('lib')

import config
import worker

mongo_uri = config.getSection("default")["mongo_uri"]
mongo = MongoClient(mongo_uri)
db = mongo.builder

change_stream = mongo.builder.build.watch()
for change in change_stream:

    if change["operationType"] == "insert":
        
        id = change["fullDocument"]["_id"]
        worker.start_build(str(id))