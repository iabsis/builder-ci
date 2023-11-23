
import os
from lib.config import Config

config = Config("default")


class Step:

    name = "defaultstep"

    def __init__(self, id, options, meta) -> None:

        # Define the project root where binary and sources will be stored
        self.build_path = os.path.join(
            os.getcwd(), config["build_location"], id)

        # Define the folder where storing source
        self.sources_path = os.path.join(self.build_path, "sources")

        # Define the folder where storing result, usually packages
        self.binary_path = os.path.join(self.build_path, "binary")

        self.options = options
        self.meta = meta
        self.id = id

    def runAction(self):
        pass

    def getMeta(self):
        pass

    def detect(self):
        pass

    def cleanupAction(self):
        pass
