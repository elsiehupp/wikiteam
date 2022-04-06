import re
import sys
import time

import requests
from exceptions import ExportAbortedError, PageMissingError
from handle_status_code import handle_status_code
from log_error import logerror
from lxml import etree
from lxml.builder import E
from uprint import uprint


def get_xml_page_core(headers: dict, params: dict, config: dict) -> str:
    """returns an XML containing params['limit'] revisions (or current only),
    ending in </mediawiki>. if retrieving params['limit'] revisions fails,
    returns a current only version. if all fail, returns the empty string
    """
    xml_string = ""
    c = 0
    maxseconds = 100  # max seconds to wait in a single sleeping
    maxretries = config["retries"]  # x retries and skip
    increment = 20  # increment every retry

    while not re.search(r"</mediawiki>", xml_string):
        if c > 0 and c < maxretries:
            wait = (
                increment * c < maxseconds and increment * c or maxseconds
            )  # incremental until maxseconds
            print(
                '    In attempt %d, XML for "%s" is wrong. Waiting %d seconds and reloading...'
                % (c, params["pages"], wait)
            )
            time.sleep(wait)
            # reducing server load requesting smallest chunks (if current then
            # limit = 1 from mother function)
            if params["limit"] > 1:
                params["limit"] = params["limit"] / 2  # half
        if c >= maxretries:
            print("    We have retried %d times" % (c))
            print(
                '    MediaWiki error for "%s", network error or whatever...'
                % (params["pages"])
            )
            if config["failfast"]:
                print("Exit, it will be for another time")
                sys.exit()
            # If it's not already what we tried: our last chance, preserve only the last revision...
            # config['current'] means that the whole dump is configured to save only the last,
            # params['current'] should mean that we've already tried this
            # fallback, because it's set by the following if and passed to
            # get_xml_page_core
            if not config["current-only"] and "current-only" not in params:
                print("    Trying to save only the last revision for this page...")
                params["current-only"] = 1
                logerror(
                    config,
                    text='Error while retrieving the full history of "%s". Trying to save only the last revision for this page'
                    % (params["pages"]),
                )
                return get_xml_page_core(headers=headers, params=params, config=config)
            else:
                print("    Saving in the errors log, and skipping...")
                logerror(
                    config,
                    text='Error while retrieving the last revision of "%s". Skipping.'
                    % (params["pages"]),
                )
                raise ExportAbortedError(config["index"])
                return ""  # empty xml
        # FIXME HANDLE HTTP Errors HERE
        try:
            with requests.Session().post(
                url=config["index"], params=params, headers=headers, timeout=10
            ) as post_response:
                handle_status_code(post_response)
                xml_string = fix_bom(post_response)
        except requests.exceptions.ConnectionError as e:
            print("    Connection error: %s" % (str(e.args[0])))
            xml_string = ""
        except requests.exceptions.ReadTimeout as e:
            print("    Read timeout: %s" % (str(e.args[0])))
            xml_string = ""
        c += 1

    return xml_string


def get_xml_page(config: dict, title: str, verbose: bool):
    """Get the full history (or current only) of a page"""

    # if server errors occurs while retrieving the full page history, it may return [oldest OK versions] + last version, excluding middle revisions, so it would be partialy truncated
    # http://www.mediawiki.org/wiki/Manual_talk:Parameters_to_Special:Export#Parameters_no_longer_in_use.3F

    limit = 1000
    truncated = False
    title_ = title
    title_ = re.sub(" ", "_", title_)
    # do not convert & into %26, title_ = re.sub('&', '%26', title_)
    try:
        params = {"title": config["export"], "pages": title_, "action": "submit"}
    except KeyError:
        params = {"title": "Special:Export", "pages": title_, "action": "submit"}
    if config["current-only"]:
        params["current-only"] = 1
        params["limit"] = 1
    else:
        params["offset"] = "1"  # 1 always < 2000s
        params["limit"] = limit
    # in other case, do not set params['templates']
    if "templates" in config and config["templates"]:
        params["templates"] = 1

    xml_string = get_xml_page_core(headers={}, params=params, config=config)
    if xml_string == "":
        raise ExportAbortedError(config["index"])
    if "</page>" not in xml_string:
        raise PageMissingError(params["title"], xml_string)
    else:
        # strip these sha1s sums which keep showing up in the export and
        # which are invalid for the XML schema (they only apply to
        # revisions)
        xml_string = re.sub(r"\n\s*<sha1>\w+</sha1>\s*\n", "\n", xml_string)
        xml_string = re.sub(r"\n\s*<sha1/>\s*\n", "\n", xml_string)

    yield xml_string.split("</page>")[0]

    # if complete history, check if this page history has > limit edits, if so, retrieve all using offset if available
    # else, warning about Special:Export truncating large page histories
    r_timestamp = "<timestamp>([^<]+)</timestamp>"

    numberofedits = 0
    numberofedits += len(re.findall(r_timestamp, xml_string))

    # search for timestamps in xml to avoid analysing empty pages like
    # Special:Allpages and the random one
    if not config["current-only"] and re.search(r_timestamp, xml_string):
        while not truncated and params["offset"]:  # next chunk
            # get the last timestamp from the acum XML
            params["offset"] = re.findall(r_timestamp, xml_string)[-1]
            try:
                xml2 = get_xml_page_core(headers={}, params=params, config=config)
            except MemoryError:
                print("The page's history exceeds our memory, halving limit.")
                params["limit"] = params["limit"] / 2
                continue

            # are there more edits in this next XML chunk or no <page></page>?
            if re.findall(r_timestamp, xml2):
                if re.findall(r_timestamp, xml2)[-1] == params["offset"]:
                    # again the same XML, this wiki does not support params in
                    # Special:Export, offer complete XML up to X edits (usually
                    # 1000)
                    print(
                        "ATTENTION: This wiki does not allow some parameters in Special:Export, therefore pages with large histories may be truncated"
                    )
                    truncated = True
                    break
                else:
                    """</namespaces>
                    </siteinfo>
                    <page>
                    <title>Main Page</title>
                    <id>15580374</id>
                    <restrictions>edit=sysop:move=sysop</restrictions> (?)
                    <revision>
                        <id>418009832</id>
                        <timestamp>2011-03-09T19:57:06Z</timestamp>
                        <contributor>
                    """
                    # offset is OK in this wiki, merge with the previous chunk
                    # of this page history and continue
                    try:
                        xml2 = xml2.split("</page>")[0]
                        yield "  <revision>" + (
                            "<revision>".join(xml2.split("<revision>")[1:])
                        )
                    except MemoryError:
                        "The page's history exceeds our memory, halving limit."
                        params["limit"] = params["limit"] / 2
                        continue
                    xml_string = xml2
                    numberofedits += len(re.findall(r_timestamp, xml_string))
            else:
                params["offset"] = ""  # no more edits in this page history
    yield "</page>\n"

    if verbose:
        print("")
        uprint("%s" % (title.strip()))

    if verbose and not config["current-only"]:
        if numberofedits == 1:
            print("(1 edit)")
        else:
            print("(%d edits)" % (numberofedits))


def make_xml_from_raw(raw_xml_string: str) -> str:
    """Discard the metadata around a <page> element in <mediawiki> string"""
    root = etree.XML(raw_xml_string)
    find = etree.XPath("//*[local-name() = 'page']")
    # The tag will inherit the namespace, like:
    # <page xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    # FIXME: pretty_print doesn't seem to work, only adds a newline
    return etree.tostring(find(root)[0], pretty_print=True)


def make_xml_from_page(page):
    """Output an XML document as a string from a page as in the API JSON"""
    try:
        p = E.page(
            E.title(str(page["title"])),
            E.ns(str(page["ns"])),
            E.id(str(page["pageid"])),
        )
        for rev in page["revisions"]:
            # Older releases like MediaWiki 1.16 do not return all fields.
            if "userid" in rev:
                userid = rev["userid"]
            else:
                userid = 0
            if "size" in rev:
                size = rev["size"]
            else:
                size = 0
            revision = E.revision(
                E.id(str(rev["revid"])),
                E.timestamp(rev["timestamp"]),
                E.text(str(rev["*"]), space="preserve", bytes=str(size)),
            )
            # The username may be deleted/suppressed
            if "user" in rev:
                revision.append(
                    E.contributor(
                        E.username(str(rev["user"])),
                        E.id(str(userid)),
                    )
                )
            else:
                revision.append(E.contributor(deleted="deleted"))
            if "comment" in rev:
                revision.append(E.comment(str(rev["comment"])))
            if "contentmodel" in rev:
                revision.append(E.model(rev["contentmodel"]))
            # Sometimes a missing parentid is not replaced with a 0 as it should.
            if "parentid" in rev:
                revision.append(E.parentid(str(rev["parentid"])))
            # The sha1 may not have been backfilled on older wikis or lack for other reasons (Wikia).
            if "sha1" in rev:
                revision.append(E.sha1(rev["sha1"]))
            p.append(revision)
    except KeyError as e:
        print(e)
        raise PageMissingError(page["title"], e)
    return etree.tostring(p, pretty_print=True, encoding="unicode")


def fix_bom(request):
    """Strip Unicode BOM"""
    if request.text.startswith("\ufeff"):
        request.encoding = "utf-8-sig"
    return request.text
