import os

import requests
from delay import delay
from util import remove_ip


def save_index_php(config: dict):
    """Save index.php as .html, to preserve license details
    available at the bottom of the page"""

    if os.path.exists("%s/index.html" % (config["path"])):
        print("index.html exists, do not overwrite")
    else:
        print("Downloading index.php (Main Page) as index.html")
        with requests.Session().post(
            url=config["index"], params={}, timeout=10
        ) as post_response:
            raw = post_response.text
        delay(config)
        raw = remove_ip(raw)
        with open("%s/index.html" % (config["path"]), "wb") as outfile:
            outfile.write(bytes(raw, "utf-8"))
