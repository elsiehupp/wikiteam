import json

import pytest
import requests

from wikiteam3.dumpgenerator.test.test_config import get_config

from .site_info import saveSiteInfo


def test_mediawiki_version_match():
    with get_config() as config:
        sess = requests.Session()
        saveSiteInfo(config, sess)
        with open(f"{config.path}/siteinfo.json") as f:
            siteInfoJson = json.load(f)
        assert "generator" in siteInfoJson["query"]["general"]
