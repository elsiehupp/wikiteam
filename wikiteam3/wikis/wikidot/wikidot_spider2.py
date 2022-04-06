#!/usr/bin/env python3

# Copyright (C) 2019 WikiTeam developers
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

import random
import re
import time

import requests


def main():
    wikis = []
    with open("wikidot-spider2.txt") as wikidot_spider2_file:
        wikis = wikidot_spider2_file.read().strip().splitlines()

    for i in range(1, 1000000):
        url = random.choice(wikis)
        urlrandom = (
            url.endswith("/")
            and (url + "random-site.php")
            or (url + "/" + "random-site.php")
        )
        print("URL exploring %s" % urlrandom)
        redirect = ""
        try:
            with requests.get(urlrandom) as get_response:
                if get_response.url and get_response.url.endswith("wikidot.com"):
                    redirect = get_response.url
                    print(redirect)
                else:
                    continue
        except Exception:
            continue

        wikis.append(redirect)

        with open("wikidot-spider2.txt", "w") as wikidot_spider2_file:
            wikis2 = []
            for wiki in wikis:
                wiki = re.sub(r"https?://www\.", "http://", wiki)
                if wiki not in wikis2:
                    wikis2.append(wiki)
            wikis = wikis2
            wikis.sort()
            wikidot_spider2_file.write("\n".join(wikis))
        print("%d wikis found" % (len(wikis)))
        sleep = random.randint(1, 5)
        print("Sleeping %d seconds" % (sleep))
        time.sleep(sleep)


if __name__ == "__main__":
    main()
