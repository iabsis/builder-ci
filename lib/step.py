
import subprocess
import os
import errno
from lib.config import Config
import lib.logs as logs
import glob
import shutil

config = Config("default")


class Step:

    name = "defaultstep"
    command = None
    mandatory_options = []

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

        # Raise an error in case of mandatory option is missing
        # TODO : Update to prevent useless logs
        self._errorOnMissingOption()

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

        # Init empty logs
        self.log_out = None
        self.log_err = None

    def _errorOnMissingOption(self):
        for option in self.mandatory_options:
            if not self.options[option['name']]:
                raise Exception(
                    f"The option {option['name']} is mandatory, here the purpose: {option['description']}")

    def _runCommand(self, command, **kargs):
        """Execute a specific command and return false if command failes to execute"""

        logs.debug("Command passed: " + str(command))

        if not "cwd" in kargs:
            kargs['cwd'] = self.sources_path,

        process = subprocess.Popen(command,
                                   **kargs,
                                   bufsize=10240,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   )

        process.wait()

        self.log_out, self.log_err = process.communicate()

        if not process.returncode == 0:
            raise Exception(
                f"An error as occured during the build: {self.log_err}")

    def _moveToBinary(self, files_to_move):
        self._moveToSpecific(files_to_move, self.binary_path)

    def _moveToSpecific(self, files_to_move, target):
        try:
            os.makedirs(target)
        except FileExistsError:
            logs.debug(f"Folder {target} already exists")
            pass

        for wildcard in files_to_move:
            for file in glob.glob(f"{self.sources_path}/{wildcard}"):
                logs.debug(f"Move file {file} to {target}")
                shutil.move(file, target)

    def runAction(self):
        pass

    def getMeta(self):
        return {}

    def detect(self):
        pass

    def cleanupAction(self):
        pass
