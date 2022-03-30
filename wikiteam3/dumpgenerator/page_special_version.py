import os
import requests

from .delay import delay
from .util import removeIP


def saveSpecialVersion(config: dict):
    """Save Special:Version as .html, to preserve extensions details"""

    if os.path.exists("%s/Special:Version.html" % (config["path"])):
        print("Special:Version.html exists, do not overwrite")
    else:
        print("Downloading Special:Version with extensions and other related info")
        with requests.Session().post(
            url=config["index"], params={"title": "Special:Version"}, timeout=10
        ) as post_response:
            raw = post_response.text
        delay(config)
        raw = removeIP(raw)
        with open("%s/Special:Version.html" % (config["path"]), "wb") as outfile:
            outfile.write(bytes(raw, "utf-8"))
