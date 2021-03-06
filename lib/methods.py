#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logs
import db
import os
import glob
import importlib
import traceback
from options import Nothing
import config
import yaml

class MethodsDb:

    def __init__(self, id, step, meta):
        self.methodFrom = "db"
        self.id = id
        self.step = step
        self.meta = meta
        methods = db.getBuilds(self.id)[step]
        self.methods = []
        if type(methods) == type({}):
            self.methods.append(methods["method"])
        elif type(methods) == type([]):
            for method in methods:
                self.methods.append(method["method"])
    
    @property
    def isMandatory(self):
        mandatory_steps = config.getAttribute("default", "mandatory_steps")
        if self.step in mandatory_steps:
            return True
        else:
            return False

    @property
    def count(self):
        return self.methods.len()

    @property
    def all(self):
        return self.methods

    @property
    def hasMethods(self):
        if self.methods == []:
            return False
        else:
            return True

    def delDuplicates(self):
        self.methods = list(dict.fromkeys(self.methods))
    
    def runAuto(self):
        if "auto" in self.methods:
            logs.debug("auto method invoked, attempt to find automatically")
            step_path = os.path.join("lib", self.step)
            method = []
            for file in glob.glob(step_path + "/*.py"):
                module = os.path.basename(file).replace(".py", "")
                options = Nothing()
                try:
                    m = importlib.import_module(self.step + "." + module)
                    if m.detect(self.id, options, self.meta):
                        self.methods.append(module)
                except:
                    logs.warning("Unable to run detect on module " + module)
                    err = traceback.format_exc()
                    logs.warning(err)
                    log = None
                    continue
            self.methods.remove("auto")
#            self.delDuplicates()

class MethodsYaml(MethodsDb):
    def __init__(self, id, step, meta, yml_file="builder.yml"):
        self.methodFrom = "yaml"
        self.id = id
        self.step = step
        self.meta = meta
        self.methods = []
        build_location = config.getSection("default")["build_location"]
        sources_path = os.path.join(build_location, self.id, "sources")
        self.yml_path = os.path.join(sources_path, yml_file)

        try:
            with open(self.yml_path, 'r') as file:
                logs.debug("File builder.yml found into project, attempt to load it")
                data = yaml.safe_load(file)[self.step]
        except FileNotFoundError:
            logs.debug("builder.yml not present")
        except KeyError:
            logs.warning("Yml file doens't contain method at step: " + self.step)
            traceback.print_exc()
        except:
            logs.warning("Loading builder.yml failed, reason: ")
            traceback.print_exc()

        try:
            if type(data) == type({}):
                self.methods.append(data["method"])
            elif type(data) == type([]):
                for method in data:
                    self.methods.append(method["method"])
        except:
            logs.warning("Yml file doesn't contain any method at step: " + self.step)
