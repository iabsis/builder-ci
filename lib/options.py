import lib.db as db
from lib.config import Config
import lib.logs as logs
import yaml
import os
import traceback

default_config = Config("default")


class OptionsDb:

    def __init__(self, id, step, method, idx=0):
        self.config = Config("method")
        self.id = id
        self.step = step
        self.method = method
        self.idx = idx

    def __getitem__(self, attribute):
        try:
            if type(db.getBuilds(self.id)[self.step]) == type({}):
                options = db.getBuilds(self.id)[self.step]["options"]
                return options[attribute]
            if type(db.getBuilds(self.id)[self.step]) == type([]):
                idx = 0
                for submethod in db.getBuilds(self.id)[self.step]:
                    if submethod["method"] == self.method and idx == self.idx:
                        options = submethod["options"]
                        return options[attribute]
                    idx = idx + 1
                raise KeyError
        except KeyError:
            options = self.config[attribute]
            if options == None:
                message = "Options requested " + attribute + " at step " + \
                    self.step + " and method " + self.method + " is missing"
                logs.warning(message)
            return options

    def __str__(self):
        return self.method


class OptionsYaml:

    def __init__(self, id, step, method, yml_file="builder.yml", idx=0):
        self.id = id
        self.step = step
        self.method = method
        self.options = {}
        self.idx = idx
        build_location = default_config["build_location"]
        sources_path = os.path.join(build_location, self.id, "sources")
        self.yml_path = os.path.join(sources_path, yml_file)

        try:
            with open(self.yml_path, 'r') as file:
                logs.debug(
                    "File builder.yml found into project, attempt to load it for method: " + self.method)
                data = yaml.safe_load(file)[self.step]
        except FileNotFoundError:
            logs.warning("Loading builder.yml failed, reason: ")
            traceback.print_exc()
        except KeyError:
            logs.warning("Yaml file doesn't contain step: " + self.step)
        except:
            logs.warning("Loading builder.yml failed, reason: ")
            traceback.print_exc()

        try:
            if type(data) == type({}):
                self.options = data["options"]
            elif type(data) == type([]):
                idx = 0
                for method in data:
                    if method["method"] == self.method and idx == self.idx:
                        self.options = method["options"]
                    idx = idx + 1
        except:
            logs.warning("Yaml file doesn't contain any options: " + self.step)

    def __getitem__(self, attribute):
        try:
            return self.options[attribute]
        except KeyError:
            options = self.config[attribute]
            if options == None:
                message = "Options requested " + attribute + " at step " + \
                    self.step + " and method " + self.method + " is missing"
                logs.warning(message)
            return options


class Nothing:
    def __getitem__(self, attribute):
        return None
