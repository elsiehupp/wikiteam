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

"""Compresses files into a 7z archive.

Args:
    archive_name (str): Name of the archive to create.
    files_to_compress (list): List of file paths to compress.
"""


def compress_files(archive_name, files_to_compress):
    with py7zr.SevenZipFile(archive_name, "w") as archive:
        for file in files_to_compress:
            archive.write(file)


"""Counts the occurrences of specific strings in given files.

Args:
    file_paths (list): List of file paths to search.
    search_strings (list): List of strings to search for in the files.
"""


def count_string_occurrences(file_paths, search_strings):
    for file_path in file_paths:
        with open(file_path) as file:
            print(f"Occurrences in {file_path}:")
            for search_string in search_strings:
                string_count = sum(1 for line in file if search_string in line)
                print(f"{search_string}: {string_count}")


"""Main function to manage the download and compression of MediaWiki content."""


def main():
    # Argument Parsing and Configuration
    parser = argparse.ArgumentParser(prog="launcher")
    parser.add_argument("wikispath")
    parser.add_argument("--generator-arg", "-g", dest="generator_args", action="append")
    args = parser.parse_args()
    wikispath = args.wikispath
    generator_args = args.generator_args if args.generator_args is not None else []

    print("Reading list of APIs from", wikispath)

    wikis = None

    with open(wikispath) as f:
        wikis = f.read().splitlines()

    print("%d APIs found" % (len(wikis)))

    # Iterate through the list of wikis
    for wiki in wikis:
        print("#" * 73)
        print("# Downloading", wiki)
        print("#" * 73)
        wiki = wiki.lower()
        # Make the prefix in standard way; api and index must be defined, not important which is which
        prefix = domain2prefix(config=Config(api=wiki, index=wiki))

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
            print("WARNING: Content of the archive not checked, we need 3.1+.")
            # TODO: Find a way like grep -q below without doing a 7z l multiple times?
            continue

        # download
        started = False  # was this wiki download started before? then resume
        wikidir = ""
        for f in os.listdir("."):
            # Does not find numbered wikidumps not verify directories
            if f.endswith("wikidump") and f.split("-")[0] == prefix:
                wikidir = f
                started = True
                break  # stop searching, dot not explore subdirectories

        subenv = dict(os.environ)
        subenv["PYTHONPATH"] = os.pathsep.join(sys.path)

        # time.sleep(60)
        # Uncomment what above and add --delay=60 in the py calls below for broken wiki farms
        # such as editthis.info, wiki-site.com, wikkii (adjust the value as needed;
        # typically they don't provide any crawl-delay value in their robots.txt).
        if started and wikidir:  # then resume
            print("Resuming download, using directory", wikidir)
            subprocess.call(
                [
                    sys.executable,
                    "-m",
                    "wikiteam3.dumpgenerator",
                    f"--api={wiki}",
                    "--xml",
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
                    break  # stop searching, dot not explore subdirectories

        prefix = wikidir.split("-wikidump")[0]

        finished = False
        if started and wikidir and prefix:
            with open(f"{wikidir}/{prefix}-history.xml") as file:
                # Checking completeness of the download
                last_line = file.readlines()[-1]
                if "</mediawiki>" in last_line:
                    finished = True
                print(
                    "No </mediawwiki> tag found: dump failed, needs fixing; resume didn't work. Exiting."
                )
        # You can also issue this on your working directory to find all incomplete dumps:
        # tail -n 1 */*-history.xml | grep -Ev -B 1 "</page>|</mediawiki>|==|^$"

        # compress
        if finished:
            time.sleep(1)
            os.chdir(wikidir)
            print("Changed directory to", os.getcwd())
            # Basic integrity check for the xml. The script doesn't actually do anything, so you should check if it's broken. Nothing can be done anyway, but redownloading.
            xml_files = [f"{prefix}-history.xml"]
            strings_to_search = [
                "<title>",
                "<page>",
                "</page>",
                "<revision>",
                "</revision>",
            ]
            count_string_occurrences(xml_files, strings_to_search)

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


# Finalization and Clean-up
# (Any necessary finalization steps or clean-up code can be placed here)

if __name__ == "__main__":
    main()
