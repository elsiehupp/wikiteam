import os

import requests

from wikiteam3.dumpgenerator.cli.delay import Delay
from wikiteam3.dumpgenerator.config import Config
from wikiteam3.utils import remove_ip


def save_special_version(config: Config, session: requests.Session):
    """Save Special:Version as .html, to preserve extensions details"""

    if os.path.exists(f"{config.path}/SpecialVersion.html"):
        print("SpecialVersion.html exists, do not overwrite")
    else:
        print("Downloading Special:Version with extensions and other related info")
        r = session.post(
            url=config.index, params={"title": "Special:Version"}, timeout=10
        )
        raw = r.text
        Delay(config=config)
        raw = str(remove_ip(raw=raw))
        with open(
            f"{config.path}/SpecialVersion.html", "w", encoding="utf-8"
        ) as outfile:
            outfile.write(raw)
