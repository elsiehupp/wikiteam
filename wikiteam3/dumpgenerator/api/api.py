import re
from urllib.parse import urljoin, urlparse

import mwclient
import requests

from wikiteam3.utils import get_user_agent

from .get_json import do_get_json


def check_api(api, session: requests.Session):
    """Checking API availability"""
    global cj
    # handle redirects
    response: (requests.Response | None) = None
    for i in range(4):
        print("Checking API...", api)
        response = session.get(
            url=api,
            params={"action": "query", "meta": "siteinfo", "format": "json"},
            timeout=30,
        )
        if i >= 4:
            break
        if response is None:
            continue
        if response.status_code == 200:
            break
        elif response.status_code < 400:
            api = response.url
        elif response.status_code > 400:
            print(
                "MediaWiki API URL not found or giving error: HTTP %d"
                % response.status_code
            )
            return None
    if response is None:
        return None
    if "MediaWiki API is not enabled for this site." in response.text:
        return None
    try:
        result = do_get_json(response)
        index = None
        if result:
            try:
                index = (
                    result["query"]["general"]["server"]
                    + result["query"]["general"]["script"]
                )
                return (True, index, api)
            except KeyError:
                print("MediaWiki API seems to work but returned no index URL")
                return (True, None, api)
    except ValueError:
        print(repr(response.text))
        print("MediaWiki API returned data we could not parse")
        return None
    return None


def mw_get_api_and_index(url: str, session: requests.Session):
    """Returns the MediaWiki API and Index.php"""

    api = ""
    index = ""
    if not session:
        session = requests.Session()  # Create a new session
        session.headers.update({"User-Agent": get_user_agent()})
    response = session.post(url=url, timeout=120)
    result = response.text

    if m := re.findall(
        r'(?im)<\s*link\s*rel="EditURI"\s*type="application/rsd\+xml"\s*href="([^>]+?)\?action=rsd"\s*/\s*>',
        result,
    ):
        api = m[0]
        if api.startswith("//"):  # gentoo wiki
            api = url.split("//")[0] + api
    if m := re.findall(
        r'<li id="ca-viewsource"[^>]*?>\s*(?:<span>)?\s*<a href="([^\?]+?)\?',
        result,
    ):
        index = m[0]
    elif m := re.findall(
        r'<li id="ca-history"[^>]*?>\s*(?:<span>)?\s*<a href="([^\?]+?)\?',
        result,
    ):
        index = m[0]
    if index:
        if index.startswith("/"):
            index = (
                urljoin(api, index.split("/")[-1])
                if api
                else urljoin(url, index.split("/")[-1])
            )
            #     api = index.split("/index.php")[0] + "/api.php"
            if index.endswith("/Main_Page"):
                index = urljoin(index, "index.php")
    elif api:
        if len(re.findall(r"/index\.php5\?", result)) > len(
            re.findall(r"/index\.php\?", result)
        ):
            index = "/".join(api.split("/")[:-1]) + "/index.php5"
        else:
            index = "/".join(api.split("/")[:-1]) + "/index.php"

    if not api and index:
        api = urljoin(index, "api.php")

    return api, index


def check_retry_api(api: str, apiclient: bool, session: requests.Session):
    """Call check_api and mwclient if necessary"""
    check = None
    try:
        check = check_api(api, session=session)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")

    if check and apiclient:
        apiurl = urlparse(api)
        try:
            site = mwclient.Site(
                apiurl.netloc,
                apiurl.path.replace("api.php", ""),
                scheme=apiurl.scheme,
                pool=session,
            )
        except KeyError:
            # Probably KeyError: 'query'
            if apiurl.scheme == "https":
                newscheme = "http"
                api = api.replace("https://", "http://")
            else:
                newscheme = "https"
                api = api.replace("http://", "https://")
            print(
                f"WARNING: The provided API URL did not work with mwclient. Switched protocol to: {newscheme}"
            )

            try:
                site = mwclient.Site(
                    apiurl.netloc,
                    apiurl.path.replace("api.php", ""),
                    scheme=newscheme,
                    pool=session,
                )
            except KeyError:
                check = False

    return check, api
