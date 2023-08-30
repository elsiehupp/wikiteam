import re
import sys
import xml.etree.ElementTree as ElementTree
from io import TextIOWrapper

import lxml.etree
import requests

from wikiteam3.dumpgenerator.api.page_titles import read_titles
from wikiteam3.dumpgenerator.cli.delay import Delay
from wikiteam3.dumpgenerator.config import Config
from wikiteam3.dumpgenerator.dump.page.xmlexport.page_xml import get_xml_page
from wikiteam3.dumpgenerator.dump.page.xmlrev.xml_revisions import get_xml_revisions
from wikiteam3.dumpgenerator.dump.xmldump.xml_header import get_xml_header
from wikiteam3.dumpgenerator.dump.xmldump.xml_truncate import (
    parse_last_page_chunk,
    truncate_xml_dump,
)
from wikiteam3.dumpgenerator.exceptions import PageMissingError
from wikiteam3.dumpgenerator.log.log_error import do_log_error
from wikiteam3.utils import clean_xml, domain_2_prefix, undo_html_entities


def do_xml_revision_dump(
    config: Config,
    session: requests.Session,
    xmlfile: TextIOWrapper,
    last_page=None,
    use_all_revisions=False,
):
    try:
        r_timestamp = "<timestamp>([^<]+)</timestamp>"
        r_arvcontinue = '<page arv_continue="(.*?)">'

        last_arv_continue = None
        for xml in get_xml_revisions(
            config=config,
            session=session,
            last_page=last_page,
            use_all_revisions=use_all_revisions,
        ):
            numrevs = len(re.findall(r_timestamp, xml))
            if arv_continue_regex := re.findall(r_arvcontinue, xml):
                current_arv_continue = arv_continue_regex[0]
                if last_arv_continue != current_arv_continue:
                    Delay(config=config)
                    last_arv_continue = current_arv_continue
            # Due to how generators work, it's expected this may be less
            xml = clean_xml(xml=xml)
            xmlfile.write(xml)

            xmltitle = re.search(r"<title>([^<]+)</title>", xml)
            if xmltitle is not None:
                title = undo_html_entities(text=xmltitle[1])
                print(f"{title}, {numrevs} edits (--xmlrevisions)")
                # Delay(config=config)
    except AttributeError as e:
        print(e)
        print("This API library version is not working")
        sys.exit()
    except UnicodeEncodeError as e:
        print(e)


def do_xml_export_dump(
    config: Config,
    session: requests.Session,
    xmlfile: TextIOWrapper,
    last_page: (ElementTree.Element | None) = None,
):
    print("\nRetrieving the XML for every page\n")

    lock = True
    start = None
    if last_page is not None:
        try:
            start = last_page.find("title").text
        except Exception:
            print(
                f"Failed to find title in last trunk XML: {lxml.etree.tostring(last_page)}"
            )
            raise
    else:
        # requested complete xml dump
        lock = False

    c = 1
    for title in read_titles(config, session=session, start=start):
        if not title:
            continue
        if title == start:  # start downloading from start, included
            lock = False
        if lock:
            continue
        Delay(config=config)
        if c % 10 == 0:
            print(f"\n->  Downloaded {c} pages\n")
        try:
            for xml in get_xml_page(
                config=config, title=title, verbose=True, session=session
            ):
                xml = clean_xml(xml=xml)
                xmlfile.write(xml)
        except PageMissingError:
            do_log_error(
                config=config,
                to_stdout=True,
                text=f'The page "{title}" was missing in the wiki (probably deleted)',
            )
        # here, XML is a correct <page> </page> chunk or
        # an empty string due to a deleted page (logged in errors log) or
        # an empty string due to an error while retrieving the page from server
        # (logged in errors log)
        c += 1


# resume used to default to False
def generate_xml_dump(config: Config, resume: bool, session: requests.Session):
    """Generates a XML dump for a list of titles or from revision IDs"""

    header, config = get_xml_header(config=config, session=session)
    footer = "</mediawiki>\n"  # new line at the end
    xmlfilename = "{}-{}-{}.xml".format(
        domain_2_prefix(config=config),
        config.date,
        "current" if config.curonly else "history",
    )
    xmlfile = None

    last_page: (ElementTree.Element | None) = None
    last_page_chunk = None
    # start != None, means we are resuming a XML dump
    if resume:
        print("Removing the last chunk of past XML dump: it is probably incomplete.")
        # truncate XML dump if it already exists
        last_page_chunk = truncate_xml_dump(f"{config.path}/{xmlfilename}")
        if not last_page_chunk.strip():
            print("Last page chunk is NULL, we'll directly start a new dump!")
            resume = False
            last_page = None
        else:
            try:
                last_page = parse_last_page_chunk(last_page_chunk)
            except lxml.etree.LxmlError:
                print("Failed to parse last page chunk: \n%s" % last_page_chunk)
                print("Cannot resume, exiting now!")
                sys.exit(1)

        print("WARNING: will try to start the download...")
        xmlfile = open(f"{config.path}/{xmlfilename}", "a", encoding="utf-8")
    else:
        print("\nRetrieving the XML for every page from the beginning\n")
        xmlfile = open(f"{config.path}/{xmlfilename}", "w", encoding="utf-8")
        xmlfile.write(header)

    if config.xmlrevisions and not config.xmlrevisions_page:
        do_xml_revision_dump(
            config, session, xmlfile, last_page, use_all_revisions=True
        )
    elif config.xmlrevisions:
        do_xml_revision_dump(
            config, session, xmlfile, last_page, use_all_revisions=False
        )
    else:  # --xml
        do_xml_export_dump(config, session, xmlfile, last_page)
    xmlfile.write(footer)
    xmlfile.close()
    print("XML dump saved at...", xmlfilename)
