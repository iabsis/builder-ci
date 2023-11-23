
import subprocess
import os
import errno
from lib.config import Config
import lib.logs as logs

config = Config("default")


class Step:

    name = "defaultstep"
    command = None

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

        # Check if a shell command is required
        # This define a self.command_path with the full path of binary
        if self.command:
            process = subprocess.Popen(["which", self.command],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            stdout, stderr = process.communicate()

            if not stdout:
                logs.error(f"ERROR: {self.command} is not installed")
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), self.command)
            else:
                self.command_path = stdout.splitlines()[0]

    def runAction(self):
        pass

    def getMeta(self):
        pass

    def detect(self):
        pass

    def cleanupAction(self):
        pass
