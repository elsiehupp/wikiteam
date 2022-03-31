#!/usr/bin/env python3

# Copyright (C) 2011-2016 WikiTeam
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

import argparse
import os
import re
import subprocess
import time
from io import BytesIO
from urllib.parse import urljoin

import requests
from dumpgenerator.domain import Domain
from dumpgenerator.user_agent import UserAgent
from internetarchive import get_item


class Uploader:

    # You need a file named keys.txt with access and secret keys,
    # in two different lines
    accesskey: str = open("keys.txt").readlines()[0].strip()
    secretkey: str = open("keys.txt").readlines()[1].strip()

    # Nothing to change below
    convertlang = {
        "ar": "Arabic",
        "de": "German",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "it": "Italian",
        "ja": "Japanese",
        "nl": "Dutch",
        "pl": "Polish",
        "pt": "Portuguese",
        "ru": "Russian",
    }

    def log(wiki, dump, msg, config: dict):
        with open("uploader-%s.log" % (config.list_file_name), "a") as log_file:
            log_file.write(f"\n{wiki};{dump};{msg}")

    def upload(wikis, config: dict, uploadeddumps=[]):
        headers = {"User-Agent": str(UserAgent())}
        dumpdir = config.wikidump_dir

        filelist = os.listdir(dumpdir)
        for wiki in wikis:
            print("#" * 73)
            print("# Uploading", wiki)
            print("#" * 73)
            wiki = wiki.lower()
            configtemp = config
            try:
                prefix = Domain(config={"api": wiki}).to_prefix()
            except KeyError:
                print("ERROR: could not produce the prefix for %s" % wiki)
            config = configtemp

            wikiname = prefix.split("-")[0]
            dumps = []
            for f in filelist:
                if f.startswith("%s-" % (wikiname)) and (
                    f.endswith("-wikidump.7z") or f.endswith("-history.xml.7z")
                ):
                    print("%s found" % f)
                    dumps.append(f)
                    # Re-introduce the break here if you only need
                    # to upload one file and the I/O is too slow
                    # break

            c = 0
            for dump in dumps:
                wikidate = dump.split("-")[1]
                item = get_item("wiki-" + wikiname)
                if dump in uploadeddumps:
                    if config.prune_directories:
                        rmline = f"rm -rf {wikiname}-{wikidate}-wikidump/"
                        # With -f the deletion might have happened before
                        # and we won't know
                        if not os.system(rmline):
                            print(f"DELETED {wikiname}-{wikidate}-wikidump/")
                    if config.prune_wikidump and dump.endswith("wikidump.7z"):
                        # Simplistic quick&dirty check for the presence
                        # of this file in the item
                        print("Checking content in previously uploaded files")
                        stdout, stderr = subprocess.Popen(
                            ["md5sum", dumpdir + "/" + dump],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        ).communicate()
                        dumphash = re.sub(" +.+\n?", "", stdout)

                        if dumphash in map(lambda x: x["md5"], item.files):
                            Uploader.log(wiki, dump, "verified", config)
                            rmline = "rm -rf %s" % dumpdir + "/" + dump
                            if not os.system(rmline):
                                print("DELETED " + dumpdir + "/" + dump)
                            print("%s was uploaded before, skipping..." % (dump))
                            continue
                        else:
                            print("ERROR: The online item misses " + dump)
                            Uploader.log(wiki, dump, "missing", config)
                            # We'll exit this if and go upload the dump
                    else:
                        print("%s was uploaded before, skipping..." % (dump))
                        continue
                else:
                    print("%s was not uploaded before" % dump)

                time.sleep(0.1)
                wikidate_text = ""
                wikidate_text += wikidate[0:4]
                wikidate_text += "-"
                wikidate_text += wikidate[4:6]
                wikidate_text += "-"
                wikidate_text += wikidate[6:8]
                print(wiki, wikiname, wikidate, dump)

                # Does the item exist already?
                ismissingitem = not item.exists

                # Logo path
                logourl = ""

                if ismissingitem or config.update:
                    # get metadata from api.php
                    # first sitename and base url
                    params = {"action": "query", "meta": "siteinfo", "format": "xml"}
                    try:
                        with requests.get(
                            url=wiki, params=params, headers=headers
                        ) as get_response:
                            if get_response.status_code < 400:
                                xml = get_response.text
                    except requests.exceptions.ConnectionError:
                        pass

                    sitename = ""
                    baseurl = ""
                    lang = ""
                    try:
                        sitename = re.findall(r"sitename=\"([^\"]+)\"", xml)[0]
                    except Exception as exception:
                        print(exception)
                    try:
                        baseurl = re.findall(r"base=\"([^\"]+)\"", xml)[0]
                    except Exception as exception:
                        print(exception)
                    try:
                        lang = re.findall(r"lang=\"([^\"]+)\"", xml)[0]
                    except Exception as exception:
                        print(exception)

                    if not sitename:
                        sitename = wikiname
                    if not baseurl:
                        baseurl = re.sub(r"(?im)/api\.php", r"", wiki)
                    # Convert protocol-relative URLs
                    baseurl = re.sub("^//", "https://", baseurl)
                    if lang:
                        lang = (
                            lang.lower() in Uploader.convertlang
                            and Uploader.convertlang[lang.lower()]
                            or lang.lower()
                        )

                    # now copyright info from API
                    params = {
                        "action": "query",
                        "meta": "siteinfo",
                        "siprop": "general|rightsinfo",
                        "format": "xml",
                    }
                    xml = ""
                    try:
                        with requests.get(
                            url=wiki, params=params, headers=headers
                        ) as get_response:
                            if get_response.status_code < 400:
                                xml = get_response.text
                    except requests.exceptions.ConnectionError:
                        pass

                    rightsinfourl = ""
                    rightsinfotext = ""
                    try:
                        rightsinfourl = re.findall(r"rightsinfo url=\"([^\"]+)\"", xml)[
                            0
                        ]
                        rightsinfotext = re.findall(r"text=\"([^\"]+)\"", xml)[0]
                    except Exception as exception:
                        print(exception)

                    raw = ""
                    try:
                        with requests.get(url=baseurl, headers=headers) as get_response:
                            if get_response.status_code < 400:
                                raw = get_response.text
                    except requests.exceptions.ConnectionError:
                        pass

                    # or copyright info from #footer in mainpage
                    if baseurl and not rightsinfourl and not rightsinfotext:
                        print("INFO: Getting license from the HTML")
                        rightsinfotext = ""
                        rightsinfourl = ""
                        try:
                            rightsinfourl = re.findall(
                                r"<link rel=\"copyright\" href=\"([^\"]+)\" />", raw
                            )[0]
                        except Exception as exception:
                            print(exception)
                        try:
                            rightsinfotext = re.findall(
                                r"<li id=\"copyright\">([^\n\r]*?)</li>", raw
                            )[0]
                        except Exception as exception:
                            print(exception)
                        if rightsinfotext and not rightsinfourl:
                            rightsinfourl = baseurl + "#footer"
                    try:
                        logourl = re.findall(
                            r'p-logo["\'][^>]*>\s*<a [^>]*background-image:\s*(?:url\()?([^;)"]+)',
                            raw,
                        )
                        if logourl:
                            logourl = logourl[0]
                        else:
                            logourl = re.findall(
                                r'"wordmark-image">[^<]*<a[^>]*>[^<]*<img src="([^"]+)"',
                                raw,
                            )[0]
                        if "http" not in logourl:
                            # Probably a relative path, construct the absolute path
                            logourl = urljoin(wiki, logourl)
                    except Exception as exception:
                        print(exception)

                    # retrieve some info from the wiki
                    wikititle = "Wiki - %s" % (sitename)  # Wiki - ECGpedia
                    """
                    <a href="http://en.ecgpedia.org/" rel="nofollow">ECGpedia,</a>:
                    a free electrocardiography (ECG) tutorial and textbook
                    to which anyone can contribute, designed for medical
                    professionals such as cardiac care nurses and physicians.
                    Dumped with <a href="https://github.com/WikiTeam/wikiteam"
                    rel="nofollow">WikiTeam</a> tools."
                    """
                    wikidesc = (
                        '<a href="%s">%s</a> dumped with '
                        '<a href="https://github.com/WikiTeam/wikiteam" '
                        'rel="nofollow">WikiTeam</a> tools.' % (baseurl, sitename)
                    )
                    wikikeys = [
                        "wiki",
                        "wikiteam",
                        "MediaWiki",
                        sitename,
                        wikiname,
                    ]  # ecg; ECGpedia; wiki; wikiteam; MediaWiki

                    if not rightsinfourl and not rightsinfotext:
                        wikikeys.append("unknowncopyright")
                    if (
                        "www.fandom.com" in rightsinfourl
                        and "/licensing" in rightsinfourl
                    ):
                        # Link the default license directly instead
                        rightsinfourl = (
                            "https://creativecommons.org/licenses/by-sa/3.0/"
                        )
                    wikilicenseurl = rightsinfourl  # http://creativecommons.org/licenses/by-nc-sa/3.0/
                    wikirights = rightsinfotext
                    """
                    e.g. http://en.ecgpedia.org/wiki/Frequently_Asked_Questions :
                    hard to fetch automatically, could be the output of API's
                    rightsinfo if it's not a usable licenseurl or
                    "Unknown copyright status" if nothing is found.
                    """

                    wikiurl = wiki  # we use api here http://en.ecgpedia.org/api.php
                else:
                    print("Item already exists.")
                    lang = "foo"
                    wikititle = "foo"
                    wikidesc = "foo"
                    wikikeys = "foo"
                    wikilicenseurl = "foo"
                    wikirights = "foo"
                    wikiurl = "foo"

                if c == 0:
                    # Item metadata
                    md = {
                        "mediatype": "web",
                        "collection": config.collection,
                        "title": wikititle,
                        "description": wikidesc,
                        "language": lang,
                        "last-updated-date": wikidate_text,
                        "subject": "; ".join(wikikeys),
                        # Keywords should be separated by ; but it doesn't
                        # matter much; the alternative is to set one per
                        # field with subject[0], subject[1], ...
                        "licenseurl": wikilicenseurl and urljoin(wiki, wikilicenseurl),
                        "rights": wikirights,
                        "originalurl": wikiurl,
                    }

                # Upload files and update metadata
                try:
                    item.upload(
                        dumpdir + "/" + dump,
                        metadata=md,
                        access_key=Uploader.accesskey,
                        secret_key=Uploader.secretkey,
                        verbose=True,
                        queue_derive=False,
                    )
                    item.modify_metadata(md)  # update
                    print(
                        "You can find it in https://archive.org/details/wiki-%s"
                        % (wikiname)
                    )
                    uploadeddumps.append(dump)
                except Exception as e:
                    print(wiki, dump, "Error when uploading?")
                    print(e)
                try:
                    Uploader.log(wiki, dump, "ok", config)
                    if logourl:
                        logo = BytesIO(requests.get(logourl, timeout=10).content)
                        if ".png" in logourl:
                            logoextension = "png"
                        elif logourl.split("."):
                            logoextension = logourl.split(".")[-1]
                        else:
                            logoextension = "unknown"
                        logoname = "wiki-" + wikiname + "_logo." + logoextension
                        item.upload(
                            {logoname: logo},
                            access_key=Uploader.accesskey,
                            secret_key=Uploader.secretkey,
                            verbose=True,
                        )
                except requests.exceptions.ConnectionError as e:
                    print(e)

                c += 1

    def __init__(self):
        parser = argparse.ArgumentParser(
            """uploader.py

    This script takes the filename of a list of wikis as argument
    and uploads their dumps to archive.org. The list must be a text
    file with the wiki's api.php URLs, one per line. Dumps must be
    in the same directory and follow the -wikidump.7z/-history.xml.7z format
    as produced by launcher.py (explained in
    https://github.com/WikiTeam/wikiteam/wiki/Tutorial#Publishing_the_dump ).
    You need a file named keys.txt with access and secret keys,
    in two different lines You also need py in the same directory as
    this script.

    Use --help to print this help."""
        )

        parser.add_argument("-pd", "--prune_directories", action="store_true")
        parser.add_argument("-pw", "--prune_wikidump", action="store_true")
        parser.add_argument("-a", "--admin", action="store_true")
        parser.add_argument("-c", "--collection", default="opensource")
        parser.add_argument("-wd", "--wikidump_dir", default=".")
        parser.add_argument("-u", "--update", action="store_true")
        parser.add_argument("list_file_name")
        config = parser.parse_args()

        self.accesskey: str = open("keys.txt").readlines()[0].strip()
        self.secretkey: str = open("keys.txt").readlines()[1].strip()

        if config.admin:
            config.collection = "wikiteam"
        uploadeddumps = []
        try:
            uploadeddumps = [
                line.split(";")[1]
                for line in open("uploader-%s.log" % (config.list_file_name))
                .read()
                .strip()
                .splitlines()
                if len(line.split(";")) > 1
            ]
        except Exception as exception:
            print(exception)
            pass
        print("%d dumps uploaded previously" % (len(uploadeddumps)))
        with open(config.list_file_name) as wiki_list_file:
            wikis = wiki_list_file.read().strip().splitlines()

        Uploader.upload(wikis, config, uploadeddumps)


if __name__ == "__main__":
    Uploader()
