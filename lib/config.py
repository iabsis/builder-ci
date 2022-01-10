from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

hard_coded_config = {
    "default_steps_order": ["sources", "patcher", "builder", "publish"],
    "optional_steps": ["patcher", "notify"],
    "default_step_end_with": ["notify"],
    "running_step_every_loop": ["notify"],
    "duplicates_meta": ["builder", "version"],
    "auto_steps": ["builder", "publish"]
}



def getSection(section):
    return(config[section])

def getAttribute(section, attribute):
    try:
        return config[section][attribute]
    except KeyError:
        if section == "default":
            return getHardCodedDefault(attribute)
        else:
            return None

def getHardCodedDefault(attribute):

    try:
        return hard_coded_config[attribute]
    except KeyError:
        if attribute == "mandatory_steps":
            mandatory_steps = []
            for step  in hard_coded_config["default_steps_order"]:
                if not step in hard_coded_config["optional_steps"]:
                    mandatory_steps.append(step)
            return mandatory_steps
        else:
            return None