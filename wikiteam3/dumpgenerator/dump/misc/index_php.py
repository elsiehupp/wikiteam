import os

import requests

from wikiteam3.dumpgenerator.cli.delay import Delay
from wikiteam3.dumpgenerator.config import Config
from wikiteam3.utils import remove_ip


def save_index_php(config: Config, session: requests.Session):
    """Save index.php as .html, to preserve license details available at the botom of the page"""

    if os.path.exists(f"{config.path}/index.html"):
        print("index.html exists, do not overwrite")
    else:
        print("Downloading index.php (Main Page) as index.html")
        r = session.post(url=config.index, params=None, timeout=10)
        raw = r.text
        Delay(config=config)
        raw = remove_ip(raw=raw)
        with open(f"{config.path}/index.html", "w", encoding="utf-8") as outfile:
            outfile.write(raw)
