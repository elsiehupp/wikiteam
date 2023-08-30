import json

import pytest
import requests

from wikiteam3.dumpgenerator.test.test_config import get_config

from .site_info import save_site_info


def test_mediawiki_1_16():
    # Object of type "Config" cannot be used with "with"
    # because it does not implement __enter__
    # with get_config("1.16.5") as config:
    config = get_config("1.16.5")
    sess = requests.Session()
    save_site_info(config, sess)
    with open(f"{config.path}/siteinfo.json") as f:
        site_info_json = json.load(f)
    assert site_info_json["query"]["general"]["generator"] == "MediaWiki 1.16.5"
