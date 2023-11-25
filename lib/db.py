#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson.int64 import Int64
import datetime
import json
from lib.config import Config

config = Config("default")

mongo_uri = config["mongo_uri"]
mongo = MongoClient(mongo_uri)
db = mongo.builder


def addBuild(data):
    data["status"] = "new"
    item = db.build.insert_one(data)
    return item.inserted_id


def getBuilds(id=None):
    if id:
        builds = db.build.find_one({"_id": ObjectId(id)})
        return builds
    else:
        builds = db.build.find()
        return builds


def reqBuild(request):
    r = db.build.find(request)
    return json.loads(dumps(r))


def isExistBuild(request):
    r = len(list(db.build.find(request)))
    return r > 0


def delBuild(id):
    db.build.delete_one({"_id": ObjectId(id)})


def setStatus(id, status):
    db.build.update_one({"_id": ObjectId(id)}, {
                        "$set": {"status": status}})


def getName(id):
    project = db.build.find_one({"_id": ObjectId(id)})
    return json.loads(dumps(project))["project"]


def setResult(id, result):
    db.build.update_one({"_id": ObjectId(id)}, {"$set": {"result": result}})


def setStep(id, step):
    db.build.update_one({"_id": ObjectId(id)}, {"$set": {"step": step}})


def setLog(id, step, method, log, err):
    t = "logs." + step + "." + method
    db.build.update_one({"_id": ObjectId(id)}, {
                        "$set": {t: {"out": log, "err": err}}})


def getLogs(id):
    return db.build.find_one({"_id": ObjectId(id)})["logs"]


def setMeta(id, meta):
    db.build.update_one({"_id": ObjectId(id)}, {"$set": {"meta": meta}})


def addWatcher(data):
    if data["project"] and data["watch"]:
        db.watcher.insert_one(data)


def getWatches(id=None):
    return db.watcher.find_one({"_id": ObjectId(id)}) if id else db.watcher.find()
