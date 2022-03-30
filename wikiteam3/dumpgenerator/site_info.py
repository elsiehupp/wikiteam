import json
import os
import requests

from .delay import delay

# from .get_json import getJSON


def saveSiteInfo(config: dict):
    """Save a file with site info"""

    if config["api"]:
        if os.path.exists("%s/siteinfo.json" % (config["path"])):
            print("siteinfo.json exists, do not overwrite")
        else:
            print("Downloading site info as siteinfo.json")

            json_result: str

            # MediaWiki 1.13+
            with requests.Session().get(
                url=config["api"],
                params={
                    "action": "query",
                    "meta": "siteinfo",
                    "siprop": "general|namespaces|statistics|dbrepllag|interwikimap|namespacealiases|specialpagealiases|usergroups|extensions|skins|magicwords|fileextensions|rightsinfo",
                    "sinumberingroup": 1,
                    "format": "json",
                },
                timeout=10,
            ) as get_response:
                json_result = get_response.json()
            # MediaWiki 1.11-1.12
            if not "query" in json_result:
                with requests.Session().get(
                    url=config["api"],
                    params={
                        "action": "query",
                        "meta": "siteinfo",
                        "siprop": "general|namespaces|statistics|dbrepllag|interwikimap",
                        "format": "json",
                    },
                    timeout=10,
                ) as get_response:
                    json_result = get_response.json()
            # MediaWiki 1.8-1.10
            if not "query" in json_result:
                with requests.Session().get(
                    url=config["api"],
                    params={
                        "action": "query",
                        "meta": "siteinfo",
                        "siprop": "general|namespaces",
                        "format": "json",
                    },
                    timeout=10,
                ) as get_response:
                    json_result = get_response.json()
            delay(config)
            with open(
                "%s/siteinfo.json" % (config["path"]), "w", encoding="utf-8"
            ) as outfile:
                outfile.write(json.dumps(json_result, indent=4, sort_keys=True))
