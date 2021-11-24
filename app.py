#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify

from bson.json_util import dumps
from bson.objectid import ObjectId
import json

import sys
sys.path.append('lib')

import config
import db

app = Flask(__name__)
#csrf = CSRFProtect()
#csrf.init_app(app)

@app.route("/build", methods = ['POST'])
def add_build():

    data = json.loads(request.data)
    newdata = {}

    try:
        newdata["project"] = data['project']
    except:
        return dumps({'message': 'error, project key is mandatory'})

    all_steps = config.getAttribute("default", "default_steps_order")
    for step in config.getAttribute("default", "default_step_end_with"):
        all_steps.append(step)

    for step in config.getAttribute("default", "default_steps_order"):
        try:
            newdata[step] = data[step]
        except KeyError:
            if step in config.getAttribute("default", "auto_steps"):
                newdata[step] = {"method": "auto"}
            elif step in config.getAttribute("default", "mandatory_steps"):
                return dumps({'message': 'error, mandatory step is mandatory: ' + step})
            else:
                newdata[step] = None

    db.addBuild(newdata)
    return dumps({'message': 'SUCCESS'})

@app.route("/build/", methods = ['GET'], defaults={'id': None})
@app.route("/build/<id>", methods = ['GET'])
def get_all_builds(id):
    try:
        builds = db.getBuilds(id)
        return jsonify(json.loads(dumps(builds)))
    except:
        return dumps({'error'})

@app.route("/build/<id>", methods = ['DELETE'])
def del_build(id):
    try:
        db.delBuild(id)
    except:
        return dumps({'error'})
    else:
        return dumps({'success'})