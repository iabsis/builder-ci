import os
import shutil
from lib.config import Config
import lib.logs as logs
config = Config("default")

build_location = config["build_location"]


class Build():

    def __init__(self, id) -> None:
        self.keep_build = False
        self.id = id

    def __enter__(self):
        logs.debug(f"Initialize project {self.id}")
        self.build_path = os.path.join(build_location, self.id)
        self.__mkBuildFolder()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__cleanBuildFolder()

    def __cleanBuildFolder(self):
        if self.keep_build:
            return

        logs.info(f"Removing build folder {self.build_path}")

        try:
            shutil.rmtree(self.build_path)
        except Exception as e:
            logs.warning(
                f"An error has occured during folder removal: {e}")

    def __mkBuildFolder(self):
        try:
            logs.debug(f"Create folder {self.build_path}")
            os.makedirs(self.build_path)
            for folder in ["sources", "binary"]:
                os.makedirs(os.path.join(self.build_path, folder))
        except FileExistsError:
            pass
