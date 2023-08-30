import contextlib
import json
import re
import sys
from typing import Tuple

import requests

from wikiteam3.dumpgenerator.config import Config
from wikiteam3.dumpgenerator.dump.page.xmlexport.page_xml import get_xml_page
from wikiteam3.dumpgenerator.exceptions import ExportAbortedError, PageMissingError
from wikiteam3.dumpgenerator.log.log_error import do_log_error


def get_xml_header(config: Config, session: requests.Session) -> Tuple[str, Config]:
    """Retrieve a random page to extract XML headers (namespace info, etc)"""
    print(config.api)
    xml = ""
    disable_special_export = config.xmlrevisions or config.xmlapiexport
    randomtitle = "Main_Page"
    if disable_special_export and config.api and config.api.endswith("api.php"):
        with contextlib.suppress(requests.exceptions.RetryError):
            xml = _extracted_from_get_xml_header_(session, config, randomtitle)
    else:
        try:
            xml = "".join(
                list(
                    get_xml_page(
                        config=config,
                        title=randomtitle,
                        verbose=False,
                        session=session,
                    )
                )
            )
        except PageMissingError as pme:
            # The <page> does not exist. Not a problem, if we get the <siteinfo>.
            xml = pme.xml
        except ExportAbortedError:
            try:
                if config.api:
                    print("Trying the local name for the Special namespace instead")
                    r = session.get(
                        url=config.api,
                        params={
                            "action": "query",
                            "meta": "siteinfo",
                            "siprop": "namespaces",
                            "format": "json",
                        },
                        timeout=120,
                    )
                    config.export = (
                        json.loads(r.text)["query"]["namespaces"]["-1"]["*"] + ":Export"
                    )
                    xml = "".join(
                        list(
                            get_xml_page(
                                config=config,
                                title=randomtitle,
                                verbose=False,
                                session=session,
                            )
                        )
                    )
            except PageMissingError as pme:
                xml = pme.xml
            except ExportAbortedError:
                pass

    header = xml.split("</mediawiki>")[0]
    if not re.match(r"\s*<mediawiki", xml):
        if config.xmlrevisions:
            # Try again the old way
            print(
                "Export test via the API failed. Wiki too old? Trying without xmlrevisions."
            )
            config.xmlrevisions = False
            header, config = get_xml_header(config=config, session=session)
        else:
            print(xml)
            print("XML export on this wiki is broken, quitting.")
            do_log_error(
                config=config,
                to_stdout=True,
                text="XML export on this wiki is broken, quitting.",
            )
            sys.exit()
    return header, config


# TODO Rename this here and in `get_xml_header`
def _extracted_from_get_xml_header_(session, config, randomtitle):
    print("Getting the XML header from the API")
    # Export and exportnowrap exist from MediaWiki 1.15, allpages from 1.8
    r = session.get(
        f"{config.api}?action=query&export=1&exportnowrap=1&list=allpages&aplimit=1",
        timeout=10,
    )
    result: str = r.text
    # Otherwise try without exportnowrap, e.g. Wikia returns a blank page on 1.19
    if not re.match(r"\s*<mediawiki", result):
        r = session.get(
            f"{config.api}?action=query&export=1&list=allpages&aplimit=1&format=json",
            timeout=10,
        )
        with contextlib.suppress(KeyError):
            result = r.json()["query"]["export"]["*"]
    if not re.match(r"\s*<mediawiki", result):
        # Do without a generator, use our usual trick of a random page title
        r = session.get(
            f"{config.api}?action=query&export=1&exportnowrap=1&titles={randomtitle}",
            timeout=10,
        )
        result = r.text
        # Again try without exportnowrap
    if not re.match(r"\s*<mediawiki", result):
        r = session.get(
            f"{config.api}?action=query&export=1&format=json&titles={randomtitle}",
            timeout=10,
        )
        with contextlib.suppress(KeyError):
            result = r.json()["query"]["export"]["*"]
    return result
