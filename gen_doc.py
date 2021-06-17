#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import re
import json

doc = {}

for python_file in glob.glob('lib/*/*.py'):

    try:
        doc
    except:
        doc = {}

    dir = os.path.dirname(python_file)
    step = os.path.split(dir)[1]

    try:
        doc[step]
    except KeyError:
        doc[step] = {}

    method = os.path.basename(python_file)

    try:
        doc[step][method]
    except KeyError:
        doc[step][method] = {}

    try:
        doc[step][method]["options"]
    except KeyError:
        doc[step][method]["options"] = []

    try:
        doc[step][method]["meta"]
    except KeyError:
        doc[step][method]["meta"] = []


    with open(python_file) as f:
        for line in f.readlines():
            pattern = re.compile(r'.*options\[\"(\w+)\"\].*')
            if pattern.match(line):
                m = pattern.search(line)
                option = m.group(1)
                doc[step][method]["options"].append(option)
        doc[step][method]["options"] = list(set(doc[step][method]["options"]))
    
    with open(python_file) as f:
        for line in f.readlines():
            pattern = re.compile(r'.*meta\[\"(\w+)\"\].*')
            if pattern.match(line):
                m = pattern.search(line)
                option = m.group(1)
                doc[step][method]["meta"].append(option)
        doc[step][method]["meta"] = list(set(doc[step][method]["meta"]))

    with open(python_file) as f:
        content = f.read()
        pattern = re.findall(r'([\'"])\1\1(.*?)\1{3}', content, re.DOTALL)
        if not pattern == []:
            doc[step][method]["doc"] = pattern[0][1]


print(json.dumps(doc, indent=4))