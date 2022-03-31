import re
from urllib.parse import urlparse

import mwclient
import requests

from .delay import delay
from .domain import Domain
from .namespaces import Namespaces
from .util import cleanHTML, undoHTMLEntities


def getPageTitlesAPI(config: dict):
    """Uses the API to get the list of page titles"""
    titles = []

    print("")
    print("Retrieving titles from the API")

    namespaces = Namespaces(config)
    for namespace_index in namespaces.namespace_indices:
        if namespace_index in config["exnamespaces"]:
            if namespace_index == "all":
                raise ValueError(
                    "Tring to skip all namespaces——you shouldn't be able to do this!"
                )
            elif namespace_index == 0:
                print(
                    "(%d)\tSkipping root namespace"
                    % (namespace_index, namespaces.namespace_dict[namespace_index])
                )
            else:
                print(
                    "(%d)\tSkipping namespace %s"
                    % (namespace_index, namespaces.namespace_dict[namespace_index])
                )
            continue

        count = 0
        if namespace_index == "all":
            print("")
            print("Retrieving titles from all namespaces")
        elif namespace_index == 0:
            print("")
            print("(%d)\tRetrieving titles from root namespace" % (namespace_index))
        else:
            print("")
            print(
                '(%d)\tRetrieving titles from namespace "%s"'
                % (namespace_index, namespaces.namespace_dict[namespace_index])
            )
        apiurl = urlparse(config["api"])
        site = mwclient.Site(
            apiurl.netloc, apiurl.path.replace("api.php", ""), scheme=apiurl.scheme
        )
        for page in site.allpages(namespace=namespace_index):
            title = page.name
            titles.append(title)
            count += 1
            yield title

        if len(titles) != len(set(titles)):
            print("Probably a loop, switching to next namespace")
            titles = list(set(titles))

        printTitlesRetrieved(count)
        delay(config)


def getPageTitlesScraper(config):
    """Scrape the list of page titles from Special:Allpages"""

    print("")
    print("Retrieving titles by scraping")

    titles = []
    namespaces = Namespaces(config=config)
    for namespace_index in namespaces.namespace_indices:
        if namespace_index == "all":
            print("")
            print("Retrieving titles from all namespaces")
        elif namespace_index == 0:
            print("")
            print(
                "(%d)\tRetrieving titles from root namespace"
                % (namespace_index, namespaces.namespace_dict[namespace_index])
            )
        else:
            print("")
            print(
                '(%d)\tRetrieving titles from namespace "%s"'
                % (namespace_index, namespaces.namespace_dict[namespace_index])
            )
        url = "{}?title=Special:Allpages&namespace={}".format(
            config["index"],
            namespace_index,
        )
        with requests.Session().get(url=url, timeout=30) as get_response:
            raw = get_response.text
        raw = cleanHTML(raw)

        r_title = 'title="(?P<title>[^>]+)">'
        r_suballpages = ""
        r_suballpages1 = '&amp;from=(?P<from>[^>]+)&amp;to=(?P<to>[^>]+)">'
        r_suballpages2 = 'Special:Allpages/(?P<from>[^>]+)">'
        r_suballpages3 = '&amp;from=(?P<from>[^>]+)" title="[^>]+">'
        if re.search(r_suballpages1, raw):
            r_suballpages = r_suballpages1
        elif re.search(r_suballpages2, raw):
            r_suballpages = r_suballpages2
        elif re.search(r_suballpages3, raw):
            r_suballpages = r_suballpages3
        else:
            pass  # perhaps no subpages

        # Should be enought subpages on Special:Allpages
        deep = 50
        count = 0
        oldfr = ""
        checked_suballpages = []
        rawacum = raw
        while r_suballpages and re.search(r_suballpages, raw) and count < deep:
            # load sub-Allpages
            match = re.compile(r_suballpages).finditer(raw)
            for i in match:
                fr = i.group("from")
                currfr = fr

                if oldfr == currfr:
                    # We are looping, exit the loop
                    pass

                if r_suballpages == r_suballpages1:
                    to = i.group("to")
                    name = f"{fr}-{to}"
                    url = "{}?title=Special:Allpages&namespace={}&from={}&to={}".format(
                        config["index"],
                        namespace_index,
                        fr,
                        to,
                    )  # do not put urllib.parse.quote in fr or to
                # fix, esta regexp no carga bien todas? o falla el r_title en
                # este tipo de subpag? (wikiindex)
                elif r_suballpages == r_suballpages2:
                    # clean &amp;namespace=\d, sometimes happens
                    fr = fr.split("&amp;namespace=")[0]
                    name = fr
                    url = "{}?title=Special:Allpages/{}&namespace={}".format(
                        config["index"],
                        name,
                        namespace_index,
                    )
                elif r_suballpages == r_suballpages3:
                    fr = fr.split("&amp;namespace=")[0]
                    name = fr
                    url = "{}?title=Special:Allpages&from={}&namespace={}".format(
                        config["index"],
                        name,
                        namespace_index,
                    )

                if name not in checked_suballpages:
                    # to avoid reload dupe subpages links
                    checked_suballpages.append(name)
                    delay(config)
                    with requests.Session().get(url=url, timeout=10) as get_response:
                        # print ('Fetching URL: ', url)
                        raw = get_response.text
                    raw = cleanHTML(raw)
                    rawacum += raw  # merge it after removed junk
                    print(
                        "    Reading",
                        name,
                        len(raw),
                        "bytes",
                        len(re.findall(r_suballpages, raw)),
                        "subpages",
                        len(re.findall(r_title, raw)),
                        "pages",
                    )

                delay(config)
            oldfr = currfr
            count += 1

        count = 0
        match = re.compile(r_title).finditer(rawacum)
        for i in match:
            title: str = undoHTMLEntities(text=i.group("title"))
            if not title.startswith("Special:"):
                if title not in titles:
                    titles.append(title)
                    count += 1
        printTitlesRetrieved(count)
    return titles


def printTitlesRetrieved(count: int):
    if count == 1:
        print("\t(%d title retrieved)" % (count))
    else:
        print("\t(%d titles retrieved)" % (count))


def fetchPageTitles(config) -> str:
    """Fetches a list of page titles and saves it to a file.
    Returns path to file with list"""
    # http://en.wikipedia.org/wiki/Special:AllPages
    # http://wiki.archiveteam.org/index.php?title=Special:AllPages
    # http://www.wikanda.es/wiki/Especial:Todas
    namespace_dict = Namespaces(config).namespace_dict
    if config["namespaces"] == ["all"]:
        print("Loading page titles from all namespaces")
    elif config["namespaces"] is not None:
        print("Loading page titles from namespaces:")
        for namespace_index in config["namespaces"]:
            if namespace_index == "all":
                continue
            print(namespace_dict[namespace_index])
    if len(config["exnamespaces"]) > 0:
        print("Excluding titles from namespaces:")
        for exnamespace_index in config["exnamespaces"]:
            if exnamespace_index == "all":
                continue
            print(namespace_dict[exnamespace_index])

    titles: str = []
    if "api" in config and config["api"]:
        try:
            titles = getPageTitlesAPI(config)
        except Exception:
            print("Error: could not get page titles from the API")
            titles = getPageTitlesScraper(config)
    elif "index" in config and config["index"]:
        titles = getPageTitlesScraper(config)

    titlesfilename = "{}-{}-titles.txt".format(
        Domain(config).to_prefix(), config["date"]
    )
    with open(
        "{}/{}".format(config["path"], titlesfilename), "wt", encoding="utf-8"
    ) as titles_file:
        count = 0
        for title in titles:
            titles_file.write(str(title) + "\n")
            count += 1
        # TODO: Sort to remove dupes? In CZ, Widget:AddThis appears two times:
        # main namespace and widget namespace.
        # We can use sort -u in UNIX, but is it worth it?
        titles_file.write("--END--\n")
    print("\nTitles saved at...", titlesfilename)

    print("%d page titles loaded" % (count))
    return titlesfilename


def readTitles(config: dict, start=None, batch=False):
    """Read title list from a file, from the title "start" """

    titlesfilename = "{}-{}-titles.txt".format(
        Domain(config).to_prefix(), config["date"]
    )
    with open(
        "{}/{}".format(config["path"], titlesfilename), encoding="utf-8"
    ) as titles_file:

        titlelist = []
        seeking = False
        if start:
            seeking = True

        for line in titles_file:
            title = str(line).strip()
            if title == "--END--":
                break
            elif seeking and title != start:
                continue
            elif seeking and title == start:
                seeking = False

            if not batch:
                yield title
            else:
                titlelist.append(title)
                if len(titlelist) < batch:
                    continue
                else:
                    yield titlelist
                    titlelist = []
