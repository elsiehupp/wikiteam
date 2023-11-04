# Copyright (C) 2011-2023 WikiTeam developers and MediaWiki Client Tools
#
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
#
# Instructions: https://github.com/mediawiki-client-tools/mediawiki-dump-generator/blob/python3/USAGE.md

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import py7zr

from wikiteam3.dumpgenerator.config import Config
from wikiteam3.utils import domain2prefix


def main():
    # Argument Parsing and Configuration
    parser = argparse.ArgumentParser(prog="launcher")
    parser.add_argument("listofapis")
    parser.add_argument("--generator-arg", "-g", dest="generator_args", action="append")
    args = parser.parse_args()
    listofapis = args.listofapis
    generator_args = args.generator_args if args.generator_args is not None else []

    print("Reading list of APIs from", listofapis)

    wikis = None

    with open(listofapis) as f:
        wikis = f.read().splitlines()

    print("%d APIs found" % (len(wikis)))

    # Iterate through the list of wikis
    for wiki in wikis:
        print("\n# Downloading", wiki)
        wiki = wiki.lower()
        # Make the prefix in standard way; api and index must be defined, not important which is which
        prefix = domain2prefix(config=Config(api=wiki, index=wiki))
        split_url = wiki.split("/")
        if len(split_url) > 3:
            prefix = split_url[2]

        print(f"56 Value of wiki: {wiki}")
        print(f"57 Value of prefix: {prefix}")

        if zipfilename := next(
            (
                f
                for f in os.listdir(".")
                if f.endswith(".7z") and f.split("-")[0] == prefix
            ),
            None,
        ):
            # Checking Download Completeness
            print(
                "Skipping... This wiki was downloaded and compressed before in",
                zipfilename,
            )
            with py7zr.SevenZipFile(zipfilename, "r") as archive:
                archivecontent = archive.getnames()
                if f"{prefix}-history.xml" not in archivecontent:
                    print("ERROR: The archive contains no history!")
                if "SpecialVersion.html" not in archivecontent:
                    print(
                        "WARNING: The archive doesn't contain SpecialVersion.html, this may indicate that the download didn't finish."
                    )
        else:
            # TODO: Find a way to check for "</mediawiki>" in last_line.
            continue

        print(f"84 Value of wiki: {wiki}")

        # download
        started = False  # was this wiki download started before? then resume
        for f in os.listdir("."):
            if f.endswith("-wikidump") and f.startswith(prefix):
                wikidir = f
                print(f"94 Value of wikidir in the loop: {wikidir}")  # Add this print statement
                started = True
                break  # stop searching, do not explore subdirectories

        print(f"98 After download, wikidir: {wikidir}")  # Add this print statement

        if not wikidir:  # If no wikidir found, continue to the next iteration
            continue

        print(f"103 Before download, wikidir: {wikidir}")

        subenv = dict(os.environ)
        subenv["PYTHONPATH"] = os.pathsep.join(sys.path)

        # time.sleep(60)
        # Uncomment what above and add --delay=60 in the py calls below for broken wiki farms
        # such as editthis.info, wiki-site.com, wikkii (adjust the value as needed;
        # typically they don't provide any crawl-delay value in their robots.txt).
        if started and wikidir:  # then resume
            print("Resuming download, using directory", wikidir)
            print(f"111 Value of wikidir: {wikidir}")
            subprocess.call(
                [
                    sys.executable,
                    "-m",
                    "wikiteam3.dumpgenerator",
                    f"--api={wiki}",
                    "--xml",
                    "--xmlrevisions",
                    "--images",
                    "--resume",
                    f"--path={wikidir}",
                ]
                + generator_args,
                shell=False,
                env=subenv,
            )
        else:  # download from scratch
            subprocess.call(
                [
                    sys.executable,
                    "-m",
                    "wikiteam3.dumpgenerator",
                    f"--api={wiki}",
                    "--xml",
                    "--xmlrevisions",
                    "--images",
                ]
                + generator_args,
                shell=False,
                env=subenv,
            )
            started = True
            # save wikidir now
            for f in os.listdir("."):
                # Does not find numbered wikidumps not verify directories
                if f.endswith("wikidump") and f.split("-")[0] == prefix:
                    wikidir = f
                    print(f"149 Value of wikidir: {wikidir}")
                    break  # stop searching, do not explore subdirectories
        wikidir = f"{prefix}-wikidump"  # Assign the correct directory name
        print(f"151 Value of wikidir: {wikidir}")
        prefix = wikidir.split("-wikidump")[0]

        finished = False
        if started and wikidir and prefix:
            with open(f"{wikidir}/{prefix}-history.xml") as file:
                print(f"157 Value of wikidir: {wikidir}")
                # Checking completeness of the download
                last_line = file.readlines()[-1]
                if "</mediawiki>" in last_line:
                    finished = True
                else:
                    print(
                    "No </mediawwiki> tag found: dump failed, needs fixing; resume didn't work. Exiting."
                    )
        # You can also issue this on your working directory to find all incomplete dumps:
        # tail -n 1 */*-history.xml | grep -Ev -B 1 "</page>|</mediawiki>|==|^$"

        # Basic integrity check for the XML. Doesn't actually do anything.
        # Check the dump manually. Redownload if it's incomplete.
        if finished:
            time.sleep(1)
            os.chdir(wikidir)
            print(f"174 Value of wikidir: {wikidir}")
            print("Changed directory to", os.getcwd())
            xml_files = [f"{prefix}-history.xml"]

            # Search and count occurrences of specific strings within the XML file
            for file_path in xml_files:
                with open(file_path) as file:
                    print(f"Occurrences in {file_path}:")
                    for search_string in ["<title>", "<page>", "</page>", "<revision>", "</revision>"]:
                        string_count = sum(1 for line in file if search_string in line)
                        print(f"{search_string}: {string_count}")

            pathHistoryTmp = Path("..", f"{prefix}-history.xml.7z.tmp")
            pathHistoryFinal = Path("..", f"{prefix}-history.xml.7z")
            pathFullTmp = Path("..", f"{prefix}-wikidump.7z.tmp")
            pathFullFinal = Path("..", f"{prefix}-wikidump.7z")

        # Make a non-solid archive with all the text and metadata at default compression. You can also add config.txt if you don't care about your computer and user names being published or you don't use full paths so that they're not stored in it.

        # Compressing history and related files
        with py7zr.SevenZipFile(pathHistoryTmp, "w") as history_archive:
            history_archive.write(f"{prefix}-history.xml")
            history_archive.write(f"{prefix}-titles.txt")
            history_archive.write("index.html")
            history_archive.write("SpecialVersion.html")
            history_archive.write("errors.log")
            history_archive.write("siteinfo.json")

        pathHistoryTmp.rename(
            pathHistoryFinal
        )  # Rename the history file if compression was successful

        # Now we add the images, if there are some, to create another archive, without recompressing everything, at the min compression rate, higher doesn't compress images much more.

        # Compressing images
        with py7zr.SevenZipFile(pathFullTmp, "w") as full_archive:
            full_archive.write(f"{prefix}-images.txt")
            full_archive.write("images/")

        pathFullTmp.rename(
            pathFullFinal
        )  # Rename the full file if compression was successful

        os.chdir("..")
        print("Changed directory to", os.getcwd())
        time.sleep(1)


if __name__ == "__main__":
    main()
