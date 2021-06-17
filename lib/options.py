import db
import config
import logs
import yaml
import os
import traceback

class OptionsDb:

    def __init__(self, id, step, method):
        self.id = id
        self.step = step
        self.method = method

    def __getitem__(self, attribute):
        try:
            if type(db.getBuilds(self.id)[self.step]) == type({}):
                options = db.getBuilds(self.id)[self.step]["options"]
                return options[attribute]
            if type(db.getBuilds(self.id)[self.step]) == type([]):
                for submethod in db.getBuilds(self.id)[self.step]:
                    if submethod["method"] == self.method:
                        options = submethod["options"]
                        return options[attribute]
                raise KeyError
        except KeyError:
            options = config.getAttribute(self.method, attribute)
            if options == None:
                message = "Options requested " + attribute + " at step " + self.step + " and method " + self.method + " is missing"
                logs.warning(message)
            return options

    def __str__(self):
        return self.method

class OptionsYaml:

    def __init__(self, id, step, method, yml_file="builder.yml"):
        self.id = id
        self.step = step
        self.method = method
        self.options = {}
        build_location = config.getSection("default")["build_location"]
        sources_path = os.path.join(build_location, self.id, "sources")
        self.yml_path = os.path.join(sources_path, yml_file)

        try:
            with open(self.yml_path, 'r') as file:
                logs.debug("File builder.yml found into project, attempt to load it for method: " + self.method)
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
                for method in data:
                    if method["method"] == self.method:
                        self.options = method["options"]
        except:
            logs.warning("Yaml file doesn't contain any options: " + self.step)

    def __getitem__(self, attribute):
        try:
            return self.options[attribute]
        except KeyError:
            options = config.getAttribute(self.method, attribute)
            if options == None:
                message = "Options requested " + attribute + " at step " + self.step + " and method " + self.method + " is missing"
                logs.warning(message)
            return options


class Nothing:
    def __getitem__(self, attribute):
        return None
        

