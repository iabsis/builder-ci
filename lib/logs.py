import logging
import config
import db
from colorama import Fore, Style


log_file = config.getSection("logging")["log_file"]
log_level = config.getSection("logging")["log_level"]
log_num_level = getattr(logging, log_level.upper(), None)


cli_level = config.getSection("logging")["cli_level"]
cli_num_level = getattr(logging, cli_level.upper(), None)


cli = logging.getLogger(__name__)
cli.setLevel(cli_num_level)

log = logging.StreamHandler()
log.setLevel(log_num_level)
streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
log.setFormatter(streamformat)

cli.addHandler(log)

def info(message):
    cli.info(message)

def warning(message):
    cli.warning(message)

def error(message):
    cli.error(message)

def debug(message):
    cli.debug(message)

def get_logs(id, line_to_keep=200, mode="cli"):
    
    logs = []

    l = db.getLogs(id)
    for step, value in l.items():
        for method, data in value.items():
            if mode == "cli":
                logs.append(Fore.GREEN + "### Step: " + step + ", Method: " + method + Style.RESET_ALL)
            else:
                #logs.append('<span class="na">' + "### Step: " + step + ", Method: " + method + "</span>")
                logs.append("### Step: " + step + ", Method: " + method)
            if data["out"]:
                try:
                    logs.extend(data["out"].decode().split("\n"))
                except:
                    logs.extend(data["out"].split("\n"))
                    pass
            if data["err"]:
                try:
                    logs.extend(data["err"].decode().split("\n"))
                except:
                    logs.extend(data["err"].split("\n"))
                    pass
            if not data["err"] and not data["out"]:
                logs.append("No log reported at this stage")


    
    line_kept = logs[-line_to_keep:]
    if mode == "cli":
        line_kept.insert(0, Fore.RED + "Keeping only last " + str(line_to_keep) + " lines..." + Style.RESET_ALL)
    else:
        #line_kept.insert(0, '<span class="k">' + "Keeping only last " + str(line_to_keep) + " lines..." + "</span>")
        line_kept.insert(0, "Keeping only last " + str(line_to_keep) + " lines...")
    joined_logs = "\n".join(line_kept)
    return joined_logs

class Log:

    def __init__(self, id, step, method):
        self.id = id
        self.step = step
        self.method = method
    
    def setLog(self, log, err):
        db.setLog(self.id, self.step, self.method, log, err)
