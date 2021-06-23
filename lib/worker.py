#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import db
import importlib
import config
import os
import shutil
import logs
import traceback
from meta import Meta
from options import OptionsDb, OptionsYaml, Nothing
from methods import MethodsDb, MethodsYaml
from datetime import datetime
import glob


class Worker:
    def __init__(self, id):
        self.id = id
        self.name = db.getName(self.id)
        self.meta = Meta(self.id)
        self.meta["start_time"] = datetime.now()
        self.meta["status"] = "running"

        logs.info(">>>> Building project ID: " + str(self.id))
        db.setStatus(self.id, self.meta["status"])

        ## Create build location
        self.__mkBuildFolder()

        ## Running of usual step from steps_orders, usually
        # fetching sources, building and publishing the code
        for step in config.getAttribute("default", "default_steps_order"):


            ## Running loop running step, usual notifications
            for loop_step in config.getAttribute("default", "running_step_every_loop"):
                self.__startStep(loop_step, force=True)


            result = self.__startStep(step)

            if not result == True:
                
                if not self.meta["status"] == "duplicate":
                    logs.error("### A fatal error has occured, stopping now the build")
                    self.status = "failed"
                    self.meta["status"] = "failed"
                    db.setStatus(self.id, self.status)
                else:
                    logs.warning("### This build already exist into DB with state success, stopping the build")
                    self.status = "duplicate"
                    db.setStatus(self.id, self.status)
                break
        else:
            self.status = "success"
            self.meta["status"] = "success"
            db.setStatus(self.id, self.status)
            logs.info(">>>> The build has finished with success")

        self.meta["end_time"] = datetime.now()
        self.meta.saveMeta()

        if self.status == "failed":
            ## Should we remove the builded folder ?
            keep_build = config.getSection("default")["keep_failed_build"]
            if keep_build == "False":
                self.__cleanUp()
        else:
            self.__cleanUp()

        ## Running post running step, usual notifications
        for end_step in config.getAttribute("default", "default_step_end_with"):
            self.__startStep(end_step, force=True)


    def __startStep(self, step, force=False):

        logs.info("### Running step: " + step)
        db.setStep(self.id, step)

        self.meta["step"] = step
        self.meta.saveMeta()

        methodsyaml = MethodsYaml(self.id, step, self.meta)
        if methodsyaml.hasMethods:
            logs.debug("Loaded methods from Yaml file")
            methods = methodsyaml
        else:
            logs.debug("Loaded methods from Db")
            methods = MethodsDb(self.id, step, self.meta)
        
        methods.runAuto()

        ## Stop in case of process is not defined and step mandatory
        if not methods.hasMethods:
            if methods.isMandatory:
                msg = "Error, there is no method defined for step: " + step
                logdb = logs.Log(self.id, step, "missing")
                logdb.setLog(None, msg)
                logs.error(msg)
                return False
            else:
                logs.warning("There is no method defined for optional step " + step)
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
            logs.debug("No build succeed (" + step + ") , stopping now")
            return False

    def __runMethod(self, step, method, options, logdb, force=False):


        ## Initialize the method
        if not method == None:
            try:
                lib = step + "." + method
                r = importlib.import_module(lib)
            except:
                logs.error("Unable to import module: " + lib)
                traceback.print_exc()
                return False
        else:
            return False

        try:
            m = r.getMeta(self.id, options, self.meta)
            if m:
                logs.debug("Got meta from step: " + str(m))
                self.meta.mergeMeta(m)
                self.meta.saveMeta()
        except:
            traceback.print_exc()

        try:
            ## This method check if a success build with same meta already exists into DB.
            logs.debug("Force argument is set to: " + str(force))
            if self.__isDuplicate() and not force:
                self.meta["status"] = "duplicate"
                self.status = "duplicate"
                logs.info("### Duplicate build detected, stopping " + method)
                return False
            result, log, err = r.runAction(self.id, options, self.meta)
        except:
            err = traceback.format_exc()
            log = None
            result = False

        ## Get and write the logs
        logdb.setLog(log, err)

        ## General action depending of the result
        if result == True:

            ## Save meta returned by step
            try:
                m = r.getMeta(self.id, options, self.meta)
                if m:
                    logs.debug("Got meta from step: " + str(m))
                    self.meta.mergeMeta(m)
            except:
                logs.warning("Unable to get meta at step " + step)
                traceback.print_exc()
            
            self.meta.saveMeta()
            
            logs.info("### Step " + step + " has finished successfully")
        else:
            logs.error("### Step " + step + " has failed with the following error")
            try:
                print(err.decode())
            except:
                print(err)

        return result

    def __mkBuildFolder(self):
        build_location = config.getSection("default")["build_location"]
        project_folder = os.path.join(build_location, self.id)
        logs.debug("Create folder " + project_folder)
        try:
            os.makedirs(project_folder)
            for folder in ["sources", "binary"]:
                os.makedirs(os.path.join(project_folder, folder))
        except FileExistsError:
            pass 

    def __cleanUp(self):
        logs.info("Removing build folder")
        build_location = config.getSection("default")["build_location"]
        fetch_path = os.path.join(build_location, self.id)
        try:
            shutil.rmtree(fetch_path)
        except:
            return False
        else:
            return True


    def __isDuplicate(self):
        request = {}
        request["project"] = self.name
        request["status"] = "success"
        for attr in config.getAttribute("default", "duplicates_meta"):
            if self.meta[attr] == None:
                return False
            request["meta." + attr] = self.meta[attr]

        logs.debug("Try to find duplicates with: " + str(request))
        result = db.isExistBuild(request)

        if result:
            return True


def start_build(id):
    Worker(id)

if __name__ == "__main__":
    Worker()