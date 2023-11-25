#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os

config = ConfigParser()

config_trial_path = [
    "config.ini",
    "/etc/crypto-assets-consolidation/config.ini"
]

for file in config_trial_path:
    if os.path.exists(file):
        config.read(file)
        break

# # This variable defines main build step components
# default_steps_order: what is steps order and steps to run
# default_step_end_with: what step is run at the end of the process
# optional_steps: don't failes on this steps
# auto_steps: what step must be guess if not defined

hard_coded_config = {
    "default_steps_order": ["sources", "patcher", "builder", "publish"],
    "optional_steps": ["patcher", "notify"],
    "default_step_end_with": ["notify"],
    "running_step_every_loop": ["notify"],
    "duplicates_meta": ["builder", "version"],
    "auto_steps": ["builder", "publish"]
}


class Config:

    def __init__(self, section="default") -> None:
        self.section = section

    def __getitem__(self, attribute):
        try:
            return config[self.section][attribute]
        except KeyError:
            if self.section == "default":
                return getHardCodedDefault(attribute)
            else:
                return None


def getHardCodedDefault(attribute):

    try:
        return hard_coded_config[attribute]
    except KeyError:
        if attribute == "mandatory_steps":
            mandatory_steps = []
            for step in hard_coded_config["default_steps_order"]:
                if not step in hard_coded_config["optional_steps"]:
                    mandatory_steps.append(step)
            return mandatory_steps
        else:
            return None
