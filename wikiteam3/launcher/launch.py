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
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from compress import compress_history, compress_images
from py7zr import SevenZipFile

from wikiteam3.dumpgenerator.config import Config
from wikiteam3.utils.checkxml import check_xml_integrity
from wikiteam3.utils.domain import domain2prefix

# This is only to check IDE configuration
# current_directory = os.getcwd()
# print("Current working directory:", current_directory)


def main():
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

    for wiki in wikis:
        print("\n# Downloading", wiki)
        wiki = wiki.lower()
        # Make the prefix in standard way; api and index must be defined, not important which is which
        prefix = domain2prefix(config=Config(api=wiki, index=wiki))

        # Use Path to construct file paths
        current_directory = Path.cwd()
        zipfilename = next(
            (
                f
                for f in current_directory.iterdir()
                if f.suffix == ".7z" and f.stem.split("-")[0] == prefix
            ),
            None,
        )
        if zipfilename:
            print(
                "Skipping... This wiki was downloaded and compressed before in",
                zipfilename,
            )
            # Get the archive's file list.
            if (sys.version_info[0] == 3) and (sys.version_info[1] > 0):
                archive_content = SevenZipFile(zipfilename, mode="r").getnames()
                # Print the values for debugging
                print("DEBUG: Prefix:", prefix)
                print("DEBUG: Search Pattern:", r"%s.+-history\.xml" % prefix)
                print("DEBUG: Archive Content:", archive_content)
                if not any(
                    re.search(r"%s.+-history\.xml" % (prefix), filename)
                    for filename in archive_content
                ):
                    # We should perhaps not create an archive in this case, but we continue anyway.
                    print("ERROR: The archive contains no history!")
                if not any(
                    re.search(r"SpecialVersion\.html", filename)
                    for filename in archive_content
                ):
                    print(
                        "WARNING: The archive doesn't contain SpecialVersion.html, this may indicate that download didn't finish."
                    )
            else:
                print(
                    "WARNING: Content of the archive not checked, needs Python 3.1 or later."
                )
                # TODO: Find a way like grep -q below without doing a 7z l multiple times?
            continue

        # download
        started = False  # was this wiki download started before? then resume
        wikidir = ""
        for f in current_directory.iterdir():
            # Ignores date stamp, doesn't check directories
            if f.name.endswith("wikidump") and f.name.split("-")[0] == prefix:
                wikidir = f.name
                started = True
                break  # stop searching, do not explore subdirectories

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
                # Ignores date stamp, doesn't check directories
                if f.endswith("wikidump") and f.split("-")[0] == prefix:
                    wikidir = f
                    break  # stop searching, do not explore subdirectories

        prefix = wikidir.split("-wikidump")[0]

        # Start of integrity check section
        # Check if the process was initiated, the directory exists, and the prefix is defined
        if started and wikidir and prefix:
            checktags, checkends, xml_info = check_xml_integrity(
                Path(wikidir) / f"{prefix}-history.xml"
            )

            if not checktags:
                print("Integrity check failed: Counts of XML elements do not match.")

            if not checkends:
                print("Integrity check failed: Closing tag </mediawiki> is missing.")

            # Print the counts of XML elements - just for info, delete later
            print("XML Element Counts:")
            for element, count in xml_info.items():
                print(f"{element}: {count}")
            # End of integrity check section

            # If both checks passed
            if checktags and checkends:
                time.sleep(1)
                os.chdir(Path(wikidir))
                print("Changed directory to", Path.cwd())

            # Start of compression section - Rewrite these comments
            # Make an archive with all the text and metadata at default compression.
            # You can also add config.txt if you don't care about your computer and user names being published or you don't use full paths so that they're not stored in it.
            # Compress history, titles, index, SpecialVersion, errors log, and siteinfo into an archive
            compress_history(prefix)
            # Compress any images and other media files into another archive
            compress_images(prefix)
            # End of compression section

            time.sleep(1)
            os.chdir("..")
            print("Changed directory to", Path.cwd())


if __name__ == "__main__":
    main()
