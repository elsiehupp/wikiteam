import json
import pytest
import requests
from wikiteam3.dumpgenerator.test.test_config import get_config
from .site_info import saveSiteInfo

def test_mediawiki_version_match():
    mediawiki_ver = "1.39.7"  # You can set this to the actual version you expect for now
    with get_config(mediawiki_ver) as config:
        sess = requests.Session()
        saveSiteInfo(config, sess)
        with open(f"{config.path}/siteinfo.json") as f:
            siteInfoJson = json.load(f)
        expected_version = siteInfoJson["query"]["general"]["generator"]
        assert expected_version.startswith("MediaWiki")
