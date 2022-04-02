import json
import re
import sys

import requests

from .exceptions import ExportAbortedError, PageMissingError
from .log_error import logerror
from .page_xml import getXMLPage


def getXMLHeader(config: dict):
    """Retrieve a random page to extract XML headers (namespace info, etc)"""
    # get the header of a random page, to attach it in the complete XML backup
    # similar to: <mediawiki xmlns="http://www.mediawiki.org/xml/export-0.3/"
    # xmlns:x....
    randomtitle = "Main_Page"  # previously AMF5LKE43MNFGHKSDMRTJ
    print(config["api"])
    xml = ""
    if config["revisions"] and config["api"] and config["api"].endswith("api.php"):
        try:
            print("Getting the XML header from the API")
            # Export and exportnowrap exist from MediaWiki 1.15, allpages from 1.18
            with requests.get(
                config["api"]
                + "?action=query&export=1&exportnowrap=1&list=allpages&aplimit=1",
                timeout=10,
            ) as get_response:
                xml = get_response.text
            # Otherwise try without exportnowrap, e.g. Wikia returns a blank page on 1.19
            if not re.match(r"\s*<mediawiki", xml):
                with requests.get(
                    config["api"]
                    + "?action=query&export=1&list=allpages&aplimit=1&format=json",
                    timeout=10,
                ) as get_response:
                    try:
                        xml = get_response.json()["query"]["export"]["*"]
                    except KeyError:
                        pass
            if not re.match(r"\s*<mediawiki", xml):
                # Do without a generator, use our usual trick of a random page title
                with requests.get(
                    config["api"]
                    + "?action=query&export=1&exportnowrap=1&titles="
                    + randomtitle,
                    timeout=10,
                ) as get_response:
                    xml = get_response.text
            # Again try without exportnowrap
            if not re.match(r"\s*<mediawiki", xml):
                with requests.get(
                    config["api"]
                    + "?action=query&export=1&format=json&titles="
                    + randomtitle,
                    timeout=10,
                ) as get_response:
                    try:
                        xml = get_response.json()["query"]["export"]["*"]
                    except KeyError:
                        pass
        except requests.exceptions.RetryError:
            pass

    else:
        try:
            xml = "".join(
                [x for x in getXMLPage(config, title=randomtitle, verbose=False)]
            )
        except PageMissingError as pme:
            # The <page> does not exist. Not a problem, if we get the <siteinfo>.
            xml = pme.xml
        # Issue 26: Account for missing "Special" namespace.
        # Hope the canonical special name has not been removed.
        # http://albens73.fr/wiki/api.php?action=query&meta=siteinfo&siprop=namespacealiases
        except ExportAbortedError:
            try:
                if config["api"]:
                    print("Trying the local name for the Special namespace instead")
                    with requests.Session().get(
                        url=config["api"],
                        params={
                            "action": "query",
                            "meta": "siteinfo",
                            "siprop": "namespaces",
                            "format": "json",
                        },
                        timeout=120,
                    ) as get_response:
                        config["export"] = (
                            json.loads(get_response.text)["query"]["namespaces"]["-1"][
                                "*"
                            ]
                            + ":Export"
                        )
                    xml = "".join(
                        [
                            x
                            for x in getXMLPage(
                                config, title=randomtitle, verbose=False
                            )
                        ]
                    )
            except PageMissingError as pme:
                xml = pme.xml
            except ExportAbortedError:
                pass

    header = xml.split("</mediawiki>")[0]
    if not re.match(r"\s*<mediawiki", xml):
        if config["revisions"]:
            # Try again the old way
            print(
                "Export test via the API failed. Wiki too old? Trying without revisions."
            )
            config["revisions"] = False
            header, config = getXMLHeader(config)
        else:
            print("XML export on this wiki is broken, quitting.")
            logerror(config, "XML export on this wiki is broken, quitting.")
            sys.exit()
    return header, config
