
import subprocess
import os
import errno
import logging
from build.models import Build
from django.conf import settings
import glob
import shutil



class StepException(Exception):
    pass

class StepAbstract:

    logger = logging.getLogger(__name__)
    name = "defaultstep"
    command = None
    required_options = [
        #"name": "option_example",
        #"description": "Description example"
    ]
    other_options = [
        # "name": "option_example",
        # "description": "Description example"
    ]

    def __init__(self, build: Build, options: dict) -> None:

        self.build = build
        self.options = options
        self.executed = False
    
    @property
    def meta(self) -> dict:
        return self.build.meta.get(self.method) if self.build.meta else None
    
    @property
    def id(self) -> str:
        return self.build.pk

    @property
    def build_path(self) -> str:
        '''Return the temporary folder path everything is done'''
        return os.path.join(
            os.getcwd(), settings.BUILD_LOCATION, str(self.id))

    @property
    def sources_path(self) -> str:
        '''Return the full folder path where are stored sources'''
        return os.path.join(self.build_path, "sources")

    @property
    def binary_path(self) -> str:
        '''Define the folder where storing result, usually packages'''
        return os.path.join(self.build_path, "binary")

    @property
    def is_healthy(self) -> bool:
        '''Return if something is missing for properly run the step'''
        return True

    @property
    def method(self):
        '''Return the method where this object is'''
        return os.path.basename(os.getcwd())

    def run(self) -> None:
        '''Abstract of main action'''
        pass

    def check_missing_options(self):
        for option in self.required_options:
            if not self.options[option['name']]:
                raise StepException(
                    f"The option {option['name']} is mandatory, here the purpose: {option['description']}")

    def _run_command(self, command, **kargs):
        """Execute a specific command and return false if command failes to execute"""

        self.logger.debug("Command passed: " + str(command))
        self.logger.debug(kargs)

        if "cwd" not in kargs:
            kargs['cwd'] = self.sources_path,

        process = subprocess.Popen(
            command,
            **kargs,
            bufsize=10240,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        process.wait()

        log_out, log_err = process.communicate()

        self.logger.debug(f"Command {command} returned: {log_out}, {log_err}")

        if process.returncode:
            raise StepException(
                f"An error as occured during the build: {log_err}")

    def _which(self, command):
        process = subprocess.Popen(["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            self.logger.warning(stderr)

        if not stdout:
            self.logger.error("ERROR: {command} is not found")
        else:
            return stdout.splitlines()[0]


    def _move_to_binary_folder(self, files_to_move):
        self._move(files_to_move, self.binary_path)

    def _move(self, files_to_move, target):
        try:
            os.makedirs(target)
        except FileExistsError:
            self.logger.debug(f"Folder {target} already exists")

        for wildcard in files_to_move:
            for file in glob.glob(f"{self.sources_path}/{wildcard}"):
                self.logger.debug(f"Move file {file} to {target}")
                shutil.move(file, target)

    @property
    def meta(self) -> dict:
        return {}