import json

import pytest
import requests

from wikiteam3.dumpgenerator.test.test_config import get_config

from .site_info import saveSiteInfo


@pytest.mark.parametrize("mediawiki_ver", ["1.39.6"])
def test_mediawiki_version_match(mediawiki_ver):
    with get_config(mediawiki_ver) as config:
        sess = requests.Session()
        saveSiteInfo(config, sess)
        with open(f"{config.path}/siteinfo.json") as f:
            siteInfoJson = json.load(f)
        assert (
            siteInfoJson["query"]["general"]["generator"]
            == f"MediaWiki {mediawiki_ver}"
        )
