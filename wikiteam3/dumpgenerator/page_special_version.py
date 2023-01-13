import os

from .delay import Delay
from .util import removeIP


def saveSpecialVersion(config={}, session=None):
    """Save Special:Version as .html, to preserve extensions details"""

    if os.path.exists("%s/Special:Version.html" % (config["path"])):
        print("Special:Version.html exists, do not overwrite")
    else:
        print("Downloading Special:Version with extensions and other related info")
        r = session.post(
            url=config["index"], params={"title": "Special:Version"}, timeout=10
        )
        raw = str(r.text)
        Delay(config=config, session=session)
        raw = str(removeIP(raw=raw))
        with open(
            "%s/Special-Version.html" % (config["path"]), "w", encoding="utf-8" # colon is invalid for a Windows file name
        ) as outfile:
            outfile.write(str(raw))
