import json
import sys


def loadConfig(config: dict, config_filename: str) -> dict:
    """Load config file"""

    try:
        with open(
            "%s/%s" % (config["path"], config_filename), "r", encoding="utf-8"
        ) as infile:
            config = json.load(infile)
    except Exception:
        print("There is no config file. we can't resume. Start a new dump.")
        sys.exit()

    return config


def saveConfig(config: dict, config_filename: str):
    """Save config file"""

    with open(
        "%s/%s" % (config["path"], config_filename), "w", encoding="utf-8"
    ) as outfile:
        json.dump(config, outfile)
