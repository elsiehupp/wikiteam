#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 WikiTeam developers
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

# Documentation for users: https://github.com/WikiTeam/wikiteam/wiki
# Documentation for developers: http://wikiteam.readthedocs.com

import csv
import datetime
import os
import random
import re
import subprocess
import sys
import time
import urllib.request
from urllib.parse import unquote

# from internetarchive import get_item

# Requirements:
# zip command (apt-get install zip)
# ia command (pip install internetarchive, and configured properly)

"""
# You need a file with access and secret keys, in two different lines
iakeysfilename = '%s/.iakeys' % (os.path.expanduser('~'))
if os.path.exists(iakeysfilename):
    accesskey = open(iakeysfilename, 'r').readlines()[0].strip()
    secretkey = open(iakeysfilename, 'r').readlines()[1].strip()
else:
    print('Error, no %s file with S3 keys for Internet Archive account' % (iakeysfilename))
    sys.exit()
"""


def saveURL(
    wiki_domain_directory_path="",
    url="",
    filename="",
    path="",
    overwrite=False,
    iteration=1,
):
    filename2 = "%s/%s" % (wiki_domain_directory_path, filename)
    if path:
        filename2 = "%s/%s/%s" % (wiki_domain_directory_path, path, filename)
    if os.path.exists(filename2):
        if not overwrite:
            print(
                "Warning: file exists on disk. Skipping download. Force download with parameter --overwrite"
            )
            return
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url, filename2)
    except Exception:
        sleep = 10  # seconds
        maxsleep = 30
        while sleep <= maxsleep:
            try:
                print("Error while retrieving: %s" % (url))
                print("Retry in %s seconds..." % (sleep))
                time.sleep(sleep)
                urllib.request.urlretrieve(url, filename2)
                return
            except Exception:
                sleep = sleep * 2
        print("Download failed")

    # sometimes wikispaces returns invalid data, redownload in that cases
    # only 'pages'. 'files' binaries are a pain to open and check
    if (os.path.exists(filename2) and "pages" in path) or (
        os.path.exists(filename2)
        and path == ""
        and filename2.split(".")[-1] in ["xml", "html", "csv"]
    ):
        sleep2 = 60 * iteration
        raw = ""
        try:
            with open(filename2, "r", encoding="utf-8") as file2:
                raw = file2.read()
        except Exception:
            with open(filename2, "r", encoding="latin-1") as file2:
                raw = file2.read()
        if re.findall(r"(?im)<title>TES and THE Status</title>", raw):
            print(
                "Warning: invalid content. Waiting %d seconds and re-downloading"
                % (sleep2)
            )
            time.sleep(sleep2)
            saveURL(
                wiki_domain_directory_path=wiki_domain_directory_path,
                url=url,
                filename=filename,
                path=path,
                overwrite=overwrite,
                iteration=iteration + 1,
            )


def undoHTMLEntities(text=""):
    """Undo some HTML codes"""

    # i guess only < > & " ' need conversion
    # http://www.w3schools.com/html/html_entities.asp
    text = re.sub("&lt;", "<", text)
    text = re.sub("&gt;", ">", text)
    text = re.sub("&amp;", "&", text)
    text = re.sub("&quot;", '"', text)
    text = re.sub("&#039;", "'", text)

    return text


def convertHTML2Wikitext(wiki_domain_directory_path="", filename="", path=""):
    wikitext = ""
    wiki_text_file_path = "%s/%s/%s" % (wiki_domain_directory_path, path, filename)
    if not os.path.exists(wiki_text_file_path):
        print("Error retrieving wikitext, page is a redirect probably")
        return
    with open(wiki_text_file_path, "r") as wiki_text_file:
        wikitext = wiki_text_file.read()
    with open(wiki_text_file_path, "w") as wiki_text_file:
        match = re.findall(
            r'(?im)<div class="WikispacesContent WikispacesBs3">\s*<pre>', wikitext
        )
        if match:
            try:
                wikitext = wikitext.split(match[0])[1].split("</pre>")[0].strip()
                wikitext = undoHTMLEntities(text=wikitext)
            except Exception:
                pass
        wiki_text_file.write(wikitext)


def downloadPage(
    wiki_domain_directory_path="", wikiurl="", pagename="", overwrite=False
):
    pagenameplus = re.sub(" ", "+", pagename)
    pagename_ = urllib.parse.quote(pagename)

    # page current revision (html & wikitext)
    pageurl = "%s/%s" % (wikiurl, pagename_)
    filename = "%s.html" % (pagenameplus)
    print("Downloading page: %s" % (filename))
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=pageurl,
        filename=filename,
        path="pages",
        overwrite=overwrite,
    )
    pageurl2 = "%s/page/code/%s" % (wikiurl, pagename_)
    filename2 = "%s.wikitext" % (pagenameplus)
    print("Downloading page: %s" % (filename2))
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=pageurl2,
        filename=filename2,
        path="pages",
        overwrite=overwrite,
    )
    convertHTML2Wikitext(
        wiki_domain_directory_path=wiki_domain_directory_path,
        filename=filename2,
        path="pages",
    )

    # csv with page history
    csvurl = "%s/page/history/%s?utable=WikiTablePageHistoryList&ut_csv=1" % (
        wikiurl,
        pagename_,
    )
    csvfilename = "%s.history.csv" % (pagenameplus)
    print("Downloading page: %s" % (csvfilename))
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=csvurl,
        filename=csvfilename,
        path="pages",
        overwrite=overwrite,
    )


def downloadFile(
    wiki_domain_directory_path="", wikiurl="", filename="", overwrite=False
):
    filenameplus = re.sub(" ", "+", filename)
    filename_ = urllib.parse.quote(filename)

    # file full resolution
    fileurl = "%s/file/view/%s" % (wikiurl, filename_)
    filename = filenameplus
    print("Downloading file: %s" % (filename))
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=fileurl,
        filename=filename,
        path="files",
        overwrite=overwrite,
    )

    # csv with file history
    csvurl = "%s/file/detail/%s?utable=WikiTablePageList&ut_csv=1" % (
        wikiurl,
        filename_,
    )
    csvfilename = "%s.history.csv" % (filenameplus)
    print("Downloading file: %s" % (csvfilename))
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=csvurl,
        filename=csvfilename,
        path="files",
        overwrite=overwrite,
    )


def downloadPagesAndFiles(wiki_domain_directory_path="", wikiurl="", overwrite=False):
    print("Downloading Pages and Files from %s" % (wikiurl))
    # csv all pages and files
    csvurl = "%s/space/content?utable=WikiTablePageList&ut_csv=1" % (wikiurl)
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=csvurl,
        filename="pages-and-files.csv",
        path="",
    )
    # download every page and file
    line_count = 0
    with open(
        "%s/pages-and-files.csv" % (wiki_domain_directory_path), "r"
    ) as pages_and_files_csv:
        line_count = len(pages_and_files_csv.read().splitlines()) - 1
        print("This wiki has %d pages and files" % (line_count))
        rows = csv.reader(pages_and_files_csv, delimiter=",", quotechar='"')

    file_count = 0
    page_count = 0
    for row in rows:
        if row[0] == "file":
            file_count += 1
            filename = row[1]
            downloadFile(
                wiki_domain_directory_path=wiki_domain_directory_path,
                wikiurl=wikiurl,
                filename=filename,
                overwrite=overwrite,
            )
        elif row[0] == "page":
            page_count += 1
            pagename = row[1]
            downloadPage(
                wiki_domain_directory_path=wiki_domain_directory_path,
                wikiurl=wikiurl,
                pagename=pagename,
                overwrite=overwrite,
            )
        if (file_count + page_count) % 10 == 0:
            print("  Progress: %d of %d" % ((file_count + page_count), line_count))
    print("")
    print("->  Downloaded %d pages" % (page_count))
    print("->  Downloaded %d files" % (file_count))


def downloadSitemap(wiki_domain_directory_path="", wikiurl="", overwrite=False):
    print("Downloading sitemap.xml")
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=wikiurl,
        filename="sitemap.xml",
        path="",
        overwrite=overwrite,
    )


def downloadMainPage(wiki_domain_directory_path="", wikiurl="", overwrite=False):
    print("Downloading index.html")
    saveURL(
        wiki_domain_directory_path=wiki_domain_directory_path,
        url=wikiurl,
        filename="index.html",
        path="",
        overwrite=overwrite,
    )


def downloadLogo(wiki_domain_directory_path="", wikiurl="", overwrite=False):
    wiki_domain_index_file_path = "%s/index.html" % (wiki_domain_directory_path)
    if os.path.exists(wiki_domain_index_file_path):
        raw = ""
        try:
            with open(
                wiki_domain_index_file_path, "r", encoding="utf-8"
            ) as wiki_domain_index_file:
                raw = wiki_domain_index_file.read()
        except Exception:
            with open(
                wiki_domain_index_file_path, "r", encoding="latin-1"
            ) as wiki_domain_index_file:
                raw = wiki_domain_index_file.read()
        match = re.findall(r'class="WikiLogo WikiElement"><img src="([^<> "]+?)"', raw)
        if match:
            logourl = match[0]
            logofilename = logourl.split("/")[-1]
            print("Downloading logo")
            saveURL(
                wiki_domain_directory_path=wiki_domain_directory_path,
                url=logourl,
                filename=logofilename,
                path="",
                overwrite=overwrite,
            )
            return logofilename
    return ""


def printhelp():
    helptext = """This script downloads (and uploads) WikiSpaces wikis.

Parameters available:

--upload: upload compressed file with downloaded wiki
--admin: add item to WikiTeam collection (if you are an admin in that collection)
--overwrite: download again even if files exists locally
--overwrite-ia: upload again to Internet Archive even if item exists there
--help: prints this help text

Examples:

python3 wikispaces.py https://mywiki.wikispaces.com
   It downloads that wiki

python3 wikispaces.py wikis.txt
   It downloads a list of wikis (file format is a URL per line)

python3 wikispaces.py https://mywiki.wikispaces.com --upload
   It downloads that wiki, compress it and uploading to Internet Archive
"""
    print(helptext)
    sys.exit()


def duckduckgo():
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)

    wikis = []
    ignorewikis = [
        "https://wikispaces.com",
        "https://www.wikispaces.com",
        "https://wikispaces.net",
        "https://www.wikispaces.net",
    ]
    for i in range(1, 100000):
        url = "https://duckduckgo.com/html/?q=%s%%20%s%%20site:wikispaces.com" % (
            random.randint(100, 5000),
            random.randint(1000, 9999),
        )
        print("URL search", url)
        try:
            html = urllib.request.urlopen(url).read().decode("utf-8")
        except Exception:
            print("Search error")
            time.sleep(30)
            continue
        html = unquote(html)
        match = re.findall(r"://([^/]+?\.wikispaces\.com)", html)
        for wiki in match:
            wiki = "https://" + wiki
            wiki = re.sub(r"https://www\.", "https://", wiki)
            if not wiki in wikis and not wiki in ignorewikis:
                wikis.append(wiki)
                yield wiki
        sleep = random.randint(5, 20)
        print("Sleeping %d seconds" % (sleep))
        time.sleep(sleep)


def main():
    upload = False
    isadmin = False
    overwrite = False
    overwriteia = False
    if len(sys.argv) < 2:
        printhelp()
    param = sys.argv[1]
    if not param:
        printhelp()
    if len(sys.argv) > 2:
        if "--upload" in sys.argv:
            upload = True
        if "--admin" in sys.argv:
            isadmin = True
        if "--overwrite" in sys.argv:
            overwrite = True
        if "--overwrite-ia" in sys.argv:
            overwriteia = True
        if "--help" in sys.argv:
            printhelp()

    wikilist = []
    if "://" in param:
        wikilist.append(param.rstrip("/"))
    elif param.lower() == "duckduckgo":
        wikilist = duckduckgo()
        # for wiki in wikilist:
        #    print(wiki)
    else:
        with open(param, "r") as wiki_list_file:
            wikilist = wiki_list_file.read().strip().splitlines()
            wikilist2 = []
            for wiki in wikilist:
                wikilist2.append(wiki.rstrip("/"))
            wikilist = wikilist2

    for wikiurl in wikilist:
        wiki_domain_directory_path = wikiurl.split("://")[1].split("/")[0]
        print("\n")
        print("#" * 40, "\n Downloading:", wikiurl)
        print("#" * 40, "\n")

        if upload and not overwriteia:
            itemid = "wiki-%s" % (wiki_domain_directory_path)
            try:
                iahtml = ""
                try:
                    iahtml = (
                        urllib.request.urlopen(
                            "https://archive.org/details/%s" % (itemid)
                        )
                        .read()
                        .decode("utf-8")
                    )
                except Exception:
                    time.sleep(10)
                    iahtml = (
                        urllib.request.urlopen(
                            "https://archive.org/details/%s" % (itemid)
                        )
                        .read()
                        .decode("utf-8")
                    )
                if iahtml and not re.findall(r"(?im)Item cannot be found", iahtml):
                    if not overwriteia:
                        print(
                            "Warning: item exists on Internet Archive. Skipping wiki. Force with parameter --overwrite-ia"
                        )
                        print(
                            "You can find it in https://archive.org/details/%s"
                            % (itemid)
                        )
                        time.sleep(1)
                        continue
            except Exception:
                pass

        dirfiles = "%s/files" % (wiki_domain_directory_path)
        if not os.path.exists(dirfiles):
            print("Creating directory %s" % (dirfiles))
            os.makedirs(dirfiles)
        dirpages = "%s/pages" % (wiki_domain_directory_path)
        if not os.path.exists(dirpages):
            print("Creating directory %s" % (dirpages))
            os.makedirs(dirpages)
        sitemapurl = "https://%s/sitemap.xml" % (wiki_domain_directory_path)

        downloadSitemap(
            wiki_domain_directory_path=wiki_domain_directory_path,
            wikiurl=sitemapurl,
            overwrite=overwrite,
        )
        if not os.path.exists("%s/sitemap.xml" % (wiki_domain_directory_path)):
            print("Error, wiki was probably deleted. Skiping wiki...")
            continue
        else:
            sitemapraw = ""
            try:
                with open(
                    "%s/sitemap.xml" % (wiki_domain_directory_path), encoding="utf-8"
                ) as site_map_xml_file:
                    sitemapraw = site_map_xml_file.read()
            except Exception:
                with open(
                    "%s/sitemap.xml" % (wiki_domain_directory_path), encoding="latin-1"
                ) as site_map_xml_file:
                    sitemapraw = site_map_xml_file.read()
            if re.search(r"(?im)<h1>This wiki has been deactivated</h1>", sitemapraw):
                print("Error, wiki was deactivated. Skiping wiki...")
                continue

        downloadMainPage(
            wiki_domain_directory_path=wiki_domain_directory_path,
            wikiurl=wikiurl,
            overwrite=overwrite,
        )
        if not os.path.exists("%s/index.html" % (wiki_domain_directory_path)):
            print("Error, wiki was probably deleted or expired. Skiping wiki...")
            continue
        else:
            indexraw = ""
            try:
                with open(
                    "%s/index.html" % (wiki_domain_directory_path), encoding="utf-8"
                ) as index_html_file:
                    indexraw = index_html_file.read()
            except Exception:
                with open(
                    "%s/index.html" % (wiki_domain_directory_path), encoding="latin-1"
                ) as index_html_file:
                    indexraw = index_html_file.read()
            if re.search(r"(?im)<h1>Subscription Expired</h1>", indexraw):
                print("Error, wiki subscription expired. Skiping wiki...")
                continue

        downloadPagesAndFiles(
            wiki_domain_directory_path=wiki_domain_directory_path,
            wikiurl=wikiurl,
            overwrite=overwrite,
        )
        logofilename = downloadLogo(
            wiki_domain_directory_path=wiki_domain_directory_path,
            wikiurl=wikiurl,
            overwrite=overwrite,
        )

        if upload:
            itemid = "wiki-%s" % (wiki_domain_directory_path)
            print("\nCompressing dump...")
            wiki_directory_path = wiki_domain_directory_path
            os.chdir(wiki_directory_path)
            print("Changed directory to", os.getcwd())
            wikizip = "%s.zip" % (wiki_domain_directory_path)
            subprocess.call(
                "zip"
                + " -r ../%s files/ pages/ index.html pages-and-files.csv sitemap.xml %s"
                % (wikizip, logofilename),
                shell=True,
            )
            os.chdir("..")
            print("Changed directory to", os.getcwd())

            print("\nUploading to Internet Archive...")
            index_file_path = "%s/index.html" % (wiki_directory_path)
            if not os.path.exists(index_file_path):
                print("\nError dump incomplete, skipping upload\n")
                continue
            index_html_string = ""
            try:
                with open(index_file_path, "r", encoding="utf-8") as index_file:
                    index_html_string = index_file.read()
            except Exception:
                with open(index_file_path, "r", encoding="latin-1") as index_file:
                    index_html_string = index_file.read()

            wikititle = ""
            try:
                wikititle = (
                    index_html_string.split("wiki: {")[1]
                    .split("}")[0]
                    .split("text: '")[1]
                    .split("',")[0]
                    .strip()
                )
            except Exception:
                wikititle = wiki_domain_directory_path
            if not wikititle:
                wikititle = wiki_domain_directory_path
            wikititle = wikititle.replace("\\'", " ")
            wikititle = wikititle.replace('\\"', " ")
            itemtitle = "Wiki - %s" % wikititle
            itemdesc = (
                '<a href="%s">%s</a> dumped with <a href="https://github.com/WikiTeam/wikiteam" rel="nofollow">WikiTeam</a> tools.'
                % (wikiurl, wikititle)
            )
            itemtags = [
                "wiki",
                "wikiteam",
                "wikispaces",
                wikititle,
                wiki_domain_directory_path.split(".wikispaces.com")[0],
                wiki_domain_directory_path,
            ]
            itemoriginalurl = wikiurl
            itemlicenseurl = ""
            match = ""
            try:
                match = re.findall(
                    r'<a rel="license" href="([^<>]+?)">',
                    index_html_string.split('<div class="WikiLicense')[1].split(
                        "</div>"
                    )[0],
                )
            except Exception:
                match = ""
            if match:
                itemlicenseurl = match[0]
            if not itemlicenseurl:
                itemtags.append("unknowncopyright")
            itemtags_ = " ".join(
                ["--metadata='subject:%s'" % (tag) for tag in itemtags]
            )
            itemcollection = isadmin and "wikiteam" or "opensource"
            itemlang = "Unknown"
            itemdate = datetime.datetime.now().strftime("%Y-%m-%d")
            itemlogo = (
                logofilename and "%s/%s" % (wiki_directory_path, logofilename) or ""
            )
            callplain = "ia upload %s %s %s --metadata='mediatype:web' --metadata='collection:%s' --metadata='title:%s' --metadata='description:%s' --metadata='language:%s' --metadata='last-updated-date:%s' --metadata='originalurl:%s' %s %s" % (
                itemid,
                wikizip,
                itemlogo and itemlogo or "",
                itemcollection,
                itemtitle,
                itemdesc,
                itemlang,
                itemdate,
                itemoriginalurl,
                itemlicenseurl
                and "--metadata='licenseurl:%s'" % (itemlicenseurl)
                or "",
                itemtags_,
            )
            print(callplain)
            subprocess.call(callplain, shell=True)

            """
            md = {
                'mediatype': 'web',
                'collection': itemcollection,
                'title': itemtitle,
                'description': itemdesc,
                'language': itemlang,
                'last-updated-date': itemdate,
                'subject': '; '.join(itemtags), 
                'licenseurl': itemlicenseurl,
                'originalurl': itemoriginalurl,
            }
            item = get_item(itemid)
            item.upload(wikizip, metadata=md, access_key=accesskey, secret_key=secretkey, verbose=True, queue_derive=False)
            item.modify_metadata(md)
            if itemlogo:
                item.upload(itemlogo, access_key=accesskey, secret_key=secretkey, verbose=True)
            """

            print("You can find it in https://archive.org/details/%s" % (itemid))
            os.remove(wikizip)


if __name__ == "__main__":
    main()
