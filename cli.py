#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('lib')

import db
import argparse
import os, json
from bson.json_util import dumps
import json
import logs

import worker

parser = argparse.ArgumentParser(description='Helper for automated Build system')
subparsers = parser.add_subparsers(help='action help', dest='action')

build_parser = subparsers.add_parser('build',
                       help='build the project')

build_parser.add_argument('--all',
                    action='store_true',
                    help='build all projects defined as new')
build_parser.add_argument('id',
                    help='id of the project to build',
                    nargs='?')

list_parser = subparsers.add_parser('list',
                        help='list the projects')

del_parser = subparsers.add_parser('remove',
                        help='list the projects')

del_parser.add_argument('id',
                    help='id of the project to remove')

get_log  = subparsers.add_parser('logs',
                        help='get logs of project')

get_log.add_argument('id',
                    help='id of the project to get logs')

args = parser.parse_args()

if args.action == "build":
    if args.all:
        builds = db.reqBuild({"status": "new"})
        for build in builds:
            worker.start_build(build['_id']['$oid'])

    elif args.id:
        builds = db.getBuilds(args.id)
        worker.start_build(args.id)

    else:
        print("Error, you must either provide --all or project id to build")
        quit()

elif args.action == "list":
    builds = db.getBuilds()
    for build in json.loads(dumps(builds)):
        print(build['_id']['$oid'] + ' ' + build['project'] + ': ' + build['status'])

elif args.action == "remove":
    db.delBuild(args.id)

elif args.action == "logs":
    print(logs.get_logs(args.id, line_to_keep=1000))

else:
    parser.print_help()