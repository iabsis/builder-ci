#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import lib.db as db
import importlib
from lib.config import Config
import lib.logs as logs
import traceback
from lib.meta import Meta
from lib.options import OptionsDb, OptionsYaml, Nothing
from lib.methods import MethodsDb, MethodsYaml
from lib.status import Status
from lib.build import Build
from datetime import datetime

config = Config("default")


class Worker:
    def __init__(self, id):
        with Build(id) as build:
            self.id = id
            self.name = db.getName(self.id)
            self.meta = Meta(self.id)
            self.meta["start_time"] = datetime.now()

            self.__setStatus(Status.running)

            # Running of usual step from steps_orders, usually
            # fetching sources, building and publishing the code
            for step in config["default_steps_order"]:

                # Running loop running step, usual notifications
                for loop_step in config["running_step_every_loop"]:
                    self.__startStep(loop_step, force=True)

                result = self.__startStep(step)

                if not result == True:

                    if not self.meta["status"] == Status.duplicate:
                        self.__setStatus(Status.failed)
                    else:
                        self.__setStatus(Status.duplicate)
                    break
            else:
                self.__setStatus(Status.success)

            self.meta["end_time"] = datetime.now()

            if self.status == Status.failed:
                # Should we remove the builded folder ?
                if bool(config["keep_failed_build"]):
                    build.keep_build = True

            # Running post running step, usual notifications
            for end_step in config["default_step_end_with"]:
                self.__startStep(end_step, force=True)

    def __setStatus(self, status: Status):
        self.status = status
        self.meta["status"] = status.name
        db.setStatus(self.id, status.name)
        logs.info(f">>>> Build status updated: {status.name}")

    def __startStep(self, step, force=False):

        logs.info("### Running step: " + step)
        db.setStep(self.id, step)

        self.meta["step"] = step

        methodsyaml = MethodsYaml(self.id, step, self.meta)
        if methodsyaml.hasMethods:
            logs.debug("Loaded methods from Yaml file")
            methods = methodsyaml
        else:
            logs.debug("Loaded methods from Db")
            methods = MethodsDb(self.id, step, self.meta)

        methods.runAuto()

        # Stop in case of process is not defined and step mandatory
        if not methods.hasMethods:
            if methods.isMandatory:
                msg = "Error, there is no method defined for step: " + step
                logdb = logs.Log(self.id, step, "missing")
                logdb.setLog(None, msg)
                logs.error(msg)
                return False
            else:
                logs.warning(
                    "There is no method defined for optional step " + step)
                return True

        results = []

        idx = 0
        for method in methods.all:
            self.meta[step] = method
            if methods.methodFrom == "db":
                options = OptionsDb(self.id, step, method, idx=idx)
            else:
                options = OptionsYaml(self.id, step, method, idx=idx)
            logdb = logs.Log(self.id, step, method)
            result = self.__runMethod(step, method, options, logdb, force)
            results.append(result)
            idx = idx + 1

        if True in results:
            logs.debug("At least one method (" + step + ") worked, continuing")
            return True
        else:
            logs.debug("No build succeed (" + step + "), stopping now")
            return False

    def __runMethod(self, step, method, options, logdb, force=False):

        # Initialize the method
        if not method == None:
            try:
                lib = step + "." + method
                imported_lib = importlib.import_module(f"lib.{lib}")
                r = imported_lib.BuildStep(self.id, options, self.meta)
            except:
                logs.error("Unable to import module: " + lib)
                traceback.print_exc()
                return False
        else:
            return False

        try:
            m = r.getMeta()
            if m:
                logs.debug("Got meta from step: " + str(m))
                self.meta.mergeMeta(m)
        except:
            traceback.print_exc()

        try:
            # This method check if a success build with same meta already exists into DB.
            logs.debug("Force argument is set to: " + str(force))
            if self.__isDuplicate() and not force:
                self.meta["status"] = "duplicate"
                self.status = Status.duplicate
                logs.info("### Duplicate build detected, stopping " + method)
                return False

            result, log, err = r.runAction()
        except:
            err = traceback.format_exc()
            log = None
            result = False

        # Get and write the logs
        logdb.setLog(log, err)

        # General action depending of the result
        if result == True:

            # Save meta returned by step
            try:
                m = r.getMeta()
                if m:
                    logs.debug("Got meta from step: " + str(m))
                    self.meta.mergeMeta(m)
            except:
                logs.warning("Unable to get meta at step " + step)
                traceback.print_exc()

            logs.info(f"### Step {step} has finished successfully")
        else:
            logs.error(f"### Step {step} has failed with the following error")
            try:
                print(err.decode())
            except:
                print(err)

        return result

    def __isDuplicate(self):
        request = {}
        request["project"] = self.name
        request["status"] = "success"
        for attr in config["duplicates_meta"]:
            if self.meta[attr] == None:
                return False
            request["meta." + attr] = self.meta[attr]

        logs.debug("Try to find duplicates with: " + str(request))
        result = db.isExistBuild(request)

        if result:
            return True


def start_build(id):
    Worker(id)
