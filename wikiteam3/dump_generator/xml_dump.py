import os
import re
import sys

from delay import delay
from domain import Domain
from exceptions import PageMissingError
from log_error import logerror
from page_titles import read_titles
from page_xml import get_xml_page
from util import clean_xml
from xml_header import get_xml_header
from xml_revisions import get_xml_revisions
from xml_truncate import truncate_xml_dump


def generate_xml_dump(config: dict, titles: str, start: str = ""):
    """Generates a XML dump for a list of titles or from revision IDs"""
    # TODO: titles is now unused.

    header, config = get_xml_header(config)
    footer = "</mediawiki>\n"  # new line at the end
    xml_file_path = os.path.join(
        config["path"],
        "%s-%s-%s.xml"
        % (
            Domain(config).to_prefix(),
            config["date"],
            config["current-only"] and "current-only" or "history",
        ),
    )
    lock = True

    if config["revisions"]:
        if start != "":
            print("WARNING: will try to start the download from title: %s" % start)
            with open(xml_file_path, "a") as xml_file:
                xml_file.write(header)
        else:
            print("")
            print("Retrieving the XML for every page from the beginning")
            with open(xml_file_path, "w") as xml_file:
                xml_file.write(header)
        try:
            r_timestamp = "<timestamp>([^<]+)</timestamp>"
            for xml in get_xml_revisions(config, start=start):
                # Due to how generators work, it's expected this may be less
                # TODO: get the page title and reuse the usual format "X title, y edits"
                print(
                    "        %d more revisions exported"
                    % len(re.findall(r_timestamp, xml))
                )
                xml = clean_xml(xml=xml)
                xml_file.write(str(xml))
        except AttributeError as e:
            print(e)
            print("This API library version is not working")
            sys.exit()
    else:
        if start not in {"", "start"}:
            print("")
            print('Retrieving the XML for every page from "%s"' % (start))
            print(
                "Removing the last chunk of past XML dump: it is probably incomplete."
            )
            truncate_xml_dump(xml_file_path)
        else:
            print("")
            print("Retrieving the XML for every page from the beginning")
            # requested complete xml dump
            lock = False
            with open(xml_file_path, "w") as xml_file:
                xml_file.write(header)

        with open(xml_file_path, "a") as xml_file:
            count = 1
            for title in read_titles(config, start):
                if not title:
                    continue
                if title == start:  # start downloading from start, included
                    lock = False
                if lock:
                    continue
                delay(config)
                if count % 10 == 0:
                    print("")
                    print("->  Downloaded %d pages" % (count))
                try:
                    for xml in get_xml_page(config=config, title=title, verbose=True):
                        xml = clean_xml(xml=xml)
                        xml_file.write(str(xml))
                except PageMissingError:
                    logerror(
                        config,
                        text='The page "%s" was missing in the wiki (probably deleted)'
                        % title,
                    )
                # here, XML is a correct <page> </page> chunk or
                # an empty string due to a deleted page (logged in errors log) or
                # an empty string due to an error while retrieving the page from server
                # (logged in errors log)
                count += 1

    with open(xml_file_path, "a") as xml_file:
        xml_file.write(footer)
    print("XML dump saved at...", xml_file_path)
