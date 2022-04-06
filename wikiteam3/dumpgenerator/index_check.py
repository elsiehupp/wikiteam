import re

import requests


def check_index(index_php_url: str, cookies_file_path: str):
    """Checking index.php availability"""
    with requests.Session().post(
        url=index_php_url, data={"title": "Special:Version"}, timeout=30
    ) as post_response:
        if not post_response.ok:
            print(
                "ERROR: The wiki returned status code HTTP %d"
                % post_response.status_code
            )
            return False
        raw = post_response.text
    print("")
    print("Checking index.php...", index_php_url)
    # Workaround for issue 71
    if (
        re.search(
            '(Special:Badtitle</a>|class="permissions-errors"|"wgCanonicalSpecialPageName":"Badtitle"|Login Required</h1>)',
            raw,
        )
        and not cookies_file_path
    ):
        print("ERROR: This wiki requires login and we are not authenticated")
        return False
    if re.search(
        '(page-Index_php|"wgPageName":"Index.php"|"firstHeading"><span dir="auto">Index.php</span>)',
        raw,
    ):
        print("Looks like the page called Index.php, not index.php itself")
        return False
    if re.search(
        '(This wiki is powered by|<h2 id="mw-version-license">|meta name="generator" content="MediaWiki|class="mediawiki)',
        raw,
    ):
        return True
    return False
