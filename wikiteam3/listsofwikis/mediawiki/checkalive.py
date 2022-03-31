#!/usr/bin/env python3

# Copyright (C) 2011-2012 WikiTeam
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Script to check if a list of wikis are alive or dead

import re
import threading
import time

import requests


def printapi(api: str):
    print(api, "is alive")
    with open("wikisalive.txt", "a") as wikis_alive_file:
        wikis_alive_file.write("%s\n" % api.strip())


def checkcore(api: str):
    with requests.Session().get(api) as get_response:

        # except URLError as reason:  # https://docs.python.org/3/library/urllib.error.html

        if not get_response.ok:

            print("%s is dead or has errors because:" % api)
            print("Error code: %d" % get_response.status_code)
            print("Reason: %s" % get_response.reason)
            print("HTTP Headers:")
            print(get_response.headers)

        # RSD is available since 1.17, bug 25648
        rsd = re.search(
            r'(?:link rel="EditURI".+href=")(?:https?:)?(.+api.php)\?action=rsd',
            get_response.text,
        )
        # Feeds are available, with varying format, in 1.8 or earlier
        feed = re.search(
            r'(?:link rel="alternate" type="application/)(?:atom|rss)(?:\+xml[^>]+href="/)([^>]*index.php)(?:\?title=[^>]+&amp;)(?:feed|format)',
            get_response.text,
        )
        # Sometimes they're missing though, this should catch the rest but goes out of <head>
        login = re.search(
            r'(?:<li id="pt-login"><a href="/)([^>]*index.php)', get_response.text
        )
        domain = re.search(r"(https?://.[^/]+/)", api)
        # TODO: Simplistic check for API. The docs page can be returned even if everything else
        # is choking on database or PHP errors (hundreds online wikis fatal on every request).
        if (
            "This is an auto-generated MediaWiki API documentation page"
            in get_response.text
        ):
            printapi(api)
        elif rsd and rsd.group(1):
            api = "http:" + rsd.group(1)
            printapi(api)
        elif feed and feed.group(1) and domain and domain.group(1):
            index = domain.group(1) + feed.group(1)
            printapi(index)
        elif login and login.group(1) and domain and domain.group(1):
            index = domain.group(1) + login.group(1)
            printapi(index)
        else:
            print("%s is not a MediaWiki wiki." % api)


def check(apis, delay):
    for api in apis:
        threading.start_new_threading(checkcore, (api,))
        time.sleep(0.1)
    time.sleep(delay + 1)


def main(delay: float = 30, limit: int = 100):
    """delay is seconds before timing out on request"""

    apis = []
    for api in open("wikistocheck.txt").read().strip().splitlines():
        if not api in apis:
            apis.append(api)
        if len(apis) >= limit:
            check(apis, delay)
            apis = []

    check(apis)
