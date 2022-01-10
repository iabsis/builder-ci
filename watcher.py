#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('lib')
from time import sleep

import config
run_every = config.getAttribute("watcher", "run_every")

import db
import importlib
import logs

if __name__ == "__main__":

    while True:
        for project in db.getWatches():
            try:
                method = project["watch"]["method"]
                options = project["watch"]["options"]
                lib = f"lib.watcher.{method}"
                method = importlib.import_module(lib)
            except KeyError as e:
                logs.error(f"Error loading method with missing key: {e}")
                continue
            
            version = method.getLastVersion(id, options)




        
        sleep(int(run_every)*60)