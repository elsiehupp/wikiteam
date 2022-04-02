import re
import time

# from .get_json import getJSON
from urllib.parse import urlsplit

import mwclient
import requests

from .user_agent import UserAgent


class ApiInfo:

    api_string: str = ""
    index_php_url: str = ""
    url: str = ""

    def __init__(self, url_string: str):
        if url_string == "":
            raise ValueError("url_string must be assigned a value.")
        if "api.php" in url_string:
            self.url = url_string[:-7]
        else:
            self.url = url_string
        self.fetch()

    def checkAPI(self) -> bool:
        """Checking API availability"""

        print("")
        print("Checking API...", self.api_string)

        with requests.Session():
            global cookie_jar
            # handle redirects
            for i in range(4):
                with requests.Session().get(
                    url=self.api_string,
                    params={"action": "query", "meta": "siteinfo", "format": "json"},
                    timeout=30,
                ) as get_response:
                    if get_response.status_code == 200:
                        break
                    elif get_response.status_code < 400:
                        response_url = get_response.url
                        self.api_string = urlsplit(response_url).path.split("/")[-1]
                    elif get_response.status_code > 400:
                        print(
                            "MediaWiki API URL not found or giving error: "
                            "HTTP %d" % get_response.status_code
                        )
                        return False
                    if (
                        "MediaWiki API is not enabled for this site."
                        in get_response.text
                    ):
                        return False
                    try:
                        json_result = get_response.json()
                        if json_result:
                            try:
                                self.index_php_url = (
                                    json_result["query"]["general"]["server"]
                                    + json_result["query"]["general"]["script"]
                                )
                                return True
                            except KeyError:
                                print(
                                    "MediaWiki API seems to work "
                                    "but returned no index URL"
                                )
                                return True
                    except ValueError:
                        print(repr(get_response.text))
                        print("MediaWiki API returned data we could not parse")
                        return False
                    return False

        return True

    def fetch(self):
        """Returns the MediaWiki API and Index.php"""

        with requests.Session() as session:
            session.headers.update({"User-Agent": str(UserAgent())})
            with session.post(url=self.url, timeout=120) as post_response:
                post_response = post_response.text

                # API
                matches = re.findall(
                    r'(?im)<\s*link\s*rel="EditURI"\s*type="application/rsd\+xml"\s*href="([^>]+?)\?action=rsd"\s*/\s*>',
                    post_response,
                )
                if matches:
                    self.api_string = matches[0]
                    if self.api_string.startswith("//"):  # gentoo wiki
                        self.api_string = self.url.split("//")[0] + self.api_string
                else:
                    pass  # build API using index and check it

                # Index.php
                matches = re.findall(
                    r'<li id="ca-viewsource"[^>]*?>\s*(?:<span>)?\s*<a href="([^\?]+?)\?',
                    post_response,
                )
                if matches:
                    self.index_php_url = matches[0]
                else:
                    matches = re.findall(
                        r'<li id="ca-history"[^>]*?>\s*(?:<span>)?\s*<a href="([^\?]+?)\?',
                        post_response,
                    )
                    if matches:
                        self.index_php_url = matches[0]
                if self.index_php_url:
                    if self.index_php_url.startswith("/"):
                        self.index_php_url = (
                            "/".join(self.api_string.split("/")[:-1])
                            + "/"
                            + self.index_php_url.split("/")[-1]
                        )
                else:
                    if self.api_string:
                        if len(re.findall(r"/index\.php5\?", post_response)) > len(
                            re.findall(r"/index\.php\?", post_response)
                        ):
                            self.index_php_url = "/".join(
                                self.api_string.split("/")[:-1]
                            )
                            self.index_php_url += "/index.php5"
                        else:
                            self.index_php_url = "/".join(
                                self.api_string.split("/")[:-1]
                            )
                            self.index_php_url += "/index.php"

    # self.api_string=, retries=, api_client=
    def checkRetryAPI(self, retries: int = 5, api_client: bool = False) -> bool:
        """Call checkAPI and mwclient if necessary"""
        with requests.Session():
            retry = 0
            retrydelay = 20
            check = False
            while retry < retries:
                try:
                    check = self.checkAPI()
                    break
                except requests.exceptions.ConnectionError as e:
                    print("Connection error: %s" % (str(e)))
                    retry += 1
                    print(
                        "Start retry attempt %d in %d seconds."
                        % (retry + 1, retrydelay)
                    )
                    time.sleep(retrydelay)

            if check and api_client:
                apiurl = urlsplit(self.api_string)
                try:
                    mwclient.Site(
                        apiurl.netloc,
                        apiurl.path.replace("api.php", ""),
                        scheme=apiurl.scheme,
                    )
                except KeyError:
                    # Probably KeyError: 'query'
                    if apiurl.scheme == "https":
                        newscheme = "http"
                        self.api_string = self.api_string.replace("https://", "http://")
                    else:
                        newscheme = "https"
                        self.api_string = self.api_string.replace("http://", "https://")
                    print(
                        "WARNING: The provided API URL did not work "
                        "with mwclient. Switched protocol to: %s" % newscheme
                    )

                    try:
                        mwclient.Site(
                            apiurl.netloc,
                            apiurl.path.replace("api.php", ""),
                            scheme=newscheme,
                        )
                    except KeyError:
                        check = False

            return check
