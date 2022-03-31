#!/usr/bin/env python3

# Copyright (C) 2016 wikiTeam
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

import csv
import random
import re
import time

import requests
from dumpgenerator.user_agent import UserAgent


def loadUsers():
    users = {}
    with open("users.txt") as users_file:
        for x in users_file.read().strip().splitlines():
            username = x.split(",")[0]
            numwikis = x.split(",")[1]
            users[username] = numwikis
    return users


def loadWikis():
    wikis = {}
    with open("wikis.txt") as wikis_file:
        for x in wikis_file.read().strip().splitlines():
            wikiname = x.split(",")[0]
            numusers = x.split(",")[1]
            wikis[wikiname] = numusers
    return wikis


def saveUsers(users):
    with open("users.txt", "w") as users_file:
        output = [f"{x},{y}" for x, y in users.items()]
        output.sort()
        output = "\n".join(output)
        users_file.write(str(output))


def saveWikis(wikis):
    with open("wikis.txt", "w") as wikis_file:
        output = [f"{x},{y}" for x, y in wikis.items()]
        output.sort()
        output = "\n".join(output)
        wikis_file.write(str(output))


def getUsers(wiki):
    wikiurl = (
        "https://%s.wikispaces.com/wiki/members?utable=WikiTableMemberList&ut_csv=1"
        % (wiki)
    )
    try:
        with requests.Session().get(
            wikiurl, headers={"User-Agent": str(UserAgent())}
        ) as get_response:
            get_response.raise_for_status()
            reader = csv.reader(get_response.text, delimiter=",", quotechar='"')
            # headers = next(reader, None)
            usersfound = {}
            for row in reader:
                usersfound[row[0]] = "?"
            return usersfound
    except Exception:
        print("Error reading", wikiurl)
        return {}


def getWikis(user):
    wikiurl = "https://www.wikispaces.com/user/view/%s" % (user)
    try:
        with requests.Session().get(
            wikiurl, headers={"User-Agent": str(UserAgent())}
        ) as get_response:
            get_response.raise_for_status()
            html = get_response.text
            if "Wikis: " in html:
                html = html.split("Wikis: ")[1].split("</div>")[0]
                wikisfound = {}
                for x in re.findall(
                    r'<a href="https://([^>]+).wikispaces.com/">', html
                ):
                    wikisfound[x] = "?"
                return wikisfound
            return {}
    except Exception:
        print("Error reading", wikiurl)
        return {}


def main():
    sleep = 0.1
    rand = 10
    users = loadUsers()
    wikis = loadWikis()

    usersc = len(users)
    wikisc = len(wikis)
    print("Loading files")
    print("Loaded", usersc, "users")
    print("Loaded", wikisc, "wikis")

    # find more users
    print("Scanning wikis for more users")
    for wiki, numusers in wikis.items():
        if numusers != "?":  # we have scanned this wiki before, skiping
            continue
        print("Scanning https://%s.wikispaces.com for users" % (wiki))
        users2 = getUsers(wiki)
        wikis[wiki] = len(users2)
        c = 0
        for x2, y2 in users2.items():
            if x2 not in users.keys():
                users[x2] = "?"
                c += 1
        print("Found %s new users" % (c))
        if c > 0:
            if random.randint(0, rand) == 0:
                saveUsers(users)
                users = loadUsers()
        if random.randint(0, rand) == 0:
            saveWikis(wikis)
        time.sleep(sleep)
    saveWikis(wikis)
    wikis = loadWikis()
    saveUsers(users)
    users = loadUsers()

    # find more wikis
    print("Scanning users for more wikis")
    for user, numwikis in users.items():
        if numwikis != "?":  # we have scanned this user before, skiping
            continue
        print("Scanning https://www.wikispaces.com/user/view/%s for wikis" % (user))
        wikis2 = getWikis(user)
        users[user] = len(wikis2)
        c = 0
        for x2, y2 in wikis2.items():
            if x2 not in wikis.keys():
                wikis[x2] = "?"
                c += 1
        print("Found %s new wikis" % (c))
        if c > 0:
            if random.randint(0, rand) == 0:
                saveWikis(wikis)
                wikis = loadWikis()
        if random.randint(0, rand) == 0:
            saveUsers(users)
        time.sleep(sleep)
    saveWikis(wikis)
    wikis = loadWikis()
    saveUsers(users)
    users = loadUsers()

    print("\nSummary:")
    print("Found", len(users) - usersc, "new users")
    print("Found", len(wikis) - wikisc, "new wikis")


if __name__ == "__main__":
    main()
