import os
import re
import requests
import sys
from urllib.parse import unquote

from .delay import delay
from .domain import Domain
from .exceptions import PageMissingError

# from .get_json import getJSON
from .handle_status_code import handleStatusCode
from .log_error import logerror
from .page_xml import getXMLPage
from .truncate import truncateFilename
from .util import cleanHTML, undoHTMLEntities


class Image:

    config: dict
    path_for_images: str

    def __init__(self, config: dict):
        self.config = config
        self.path_for_images = "%s/images" % (config["path"])

    def getXMLFileDesc(self, title: str):
        """Get XML for image description page"""
        self.config["current-only"] = 1  # tricky to get only the most recent desc
        return "".join(
            [x for x in getXMLPage(config=self.config, title=title, verbose=False)]
        )

    def generateImageDump(
        self,
        other: dict,
        images: dict,
        start: str,
    ):
        """Save files and descriptions using a file list"""

        # fix use subdirectories md5
        print("")
        print('Retrieving images from "%s"' % (start and start or "start"))
        if not os.path.isdir(self.path_for_images):
            print('Creating "%s" directory' % (self.path_for_images))
            os.makedirs(self.path_for_images)

        count = 0
        lock = True
        if not start:
            lock = False
        for filename, url, uploader in images:
            if filename == start:  # start downloading from start (included)
                lock = False
            if lock:
                continue
            delay(self.config)

            # saving file
            # truncate filename if length > 100 (100 + 32 (md5) = 132 < 143 (crash
            # limit). Later .desc is added to filename, so better 100 as max)
            filename2 = unquote(filename)
            if len(filename2) > other["filenamelimit"]:
                # split last . (extension) and then merge
                filename2 = truncateFilename(other, filename=filename2)
                print("Filename is too long, truncating. Now it is:", filename2)
            filename3 = os.path.join(self.path_for_images, filename2)
            try:
                with open(filename3, "wb") as imagefile:

                    with requests.Session().head(
                        url=url, allow_redirects=True
                    ) as header_response:
                        original_url_redirected = len(header_response.history) > 0

                        if original_url_redirected:
                            # print 'Site is redirecting us to: ', header_response.url
                            original_url = url
                            url = header_response.url

                    with requests.Session().get(
                        url=url, allow_redirects=False
                    ) as get_response:

                        # Try to fix a broken HTTP to HTTPS redirect
                        if get_response.status_code == 404 and original_url_redirected:
                            if (
                                original_url.split("://")[0] == "http"
                                and url.split("://")[0] == "https"
                            ):
                                url = "https://" + original_url.split("://")[1]
                                # print 'Maybe a broken http to https redirect, trying ', url
                                with requests.Session().get(
                                    url=url, allow_redirects=False
                                ) as second_get_response:
                                    self.log404(
                                        status_code=second_get_response.status_code,
                                        filename=filename2,
                                        url=url,
                                    )
                                    imagefile.write(second_get_response.content)

                        else:
                            self.log404(
                                status_code=get_response.status_code,
                                filename=filename2,
                                url=url,
                            )
                            imagefile.write(get_response.content)
            except OSError:
                logerror(
                    self.config,
                    text=u"File %s could not be created by OS" % (filename3),
                )

            with requests.Session().head(
                url=url, allow_redirects=True
            ) as header_response:
                original_url_redirected = len(header_response.history) > 0

                if original_url_redirected:
                    # print 'Site is redirecting us to: ', header_response.url
                    original_url = url
                    url = header_response.url

            with requests.Session().get(url=url, allow_redirects=False) as get_response:
                # Try to fix a broken HTTP to HTTPS redirect
                if get_response.status_code == 404 and original_url_redirected:
                    if (
                        original_url.split("://")[0] == "http"
                        and url.split("://")[0] == "https"
                    ):
                        url = "https://" + original_url.split("://")[1]
                        # print 'Maybe a broken http to https redirect, trying ', url
                        with requests.Session().get(
                            url=url, allow_redirects=False
                        ) as second_get_response:
                            self.log404(
                                status_code=second_get_response.status_code,
                                filename=filename2,
                                url=url,
                            )

                self.log404(
                    status_code=get_response.status_code, filename=filename2, url=url
                )

                self.saveDescription(get_response=get_response, filename=filename2)

            delay(self.config)
            count += 1
            if count % 10 == 0:
                print("")
                print("->  Downloaded %d images" % (count))

        print("")
        print("->  Downloaded %d images" % (count))

    def log404(self, status_code: int, filename: str, url: str):
        if status_code == 404:
            logerror(
                self.config, text=u"File %s at URL %s is missing" % (filename, url)
            )

    def saveDescription(self, filename: str):
        # saving description if any
        try:
            title = u"Image:%s" % (filename)
            if (
                self.config["revisions"]
                and self.config["api"]
                and self.config["api"].endswith("api.php")
            ):
                with requests.Session().get(
                    self.config["api"]
                    + u"?action=query&export&exportnowrap&titles=%s" % title
                ) as get_response:
                    xmlfiledesc = get_response.text
            else:
                xmlfiledesc = Image.getXMLFileDesc(
                    self.config, title=title
                )  # use Image: for backwards compatibility
        except PageMissingError:
            xmlfiledesc = ""
            logerror(
                self.config,
                text=u'The page "%s" was missing in the wiki (probably deleted)'
                % (str(title)),
            )

        try:
            with open(
                "%s/%s.desc" % (self.path_for_images, filename), "w", encoding="utf-8"
            ) as image_description_file:
                # <text xml:space="preserve" bytes="36">Banner featuring SG1, SGA, SGU teams</text>
                if not re.search(r"</page>", xmlfiledesc):
                    # failure when retrieving desc? then save it as empty .desc
                    xmlfiledesc = ""

                # Fixup the XML
                if xmlfiledesc != "" and not re.search(r"</mediawiki>", xmlfiledesc):
                    xmlfiledesc += "</mediawiki>"

                image_description_file.write(str(xmlfiledesc))
        except OSError:
            logerror(
                self.config,
                text=u"File %s/%s.desc could not be created by OS"
                % (self.path_for_images, filename),
            )

    def getImageNames(self):
        """Get list of image names"""

        print("")
        print("Retrieving image filenames")
        images = []
        if "api" in self.config and self.config["api"]:
            images = Image.getImageNamesAPI(self.config)
        elif "index" in self.config and self.config["index"]:
            images = Image.getImageNamesScraper(self.config)

        # images = list(set(images)) # it is a list of lists
        images.sort()

        print("%d image names loaded" % (len(images)))
        return images

    def getImageNamesScraper(self):
        """Retrieve file list: filename, url, uploader"""

        # (?<! http://docs.python.org/library/re.html
        r_next = r"(?<!&amp;dir=prev)&amp;offset=(?P<offset>\d+)&amp;"
        images = []
        offset = "29990101000000"  # january 1, 2999
        limit = 5000
        retries = self.config["retries"]
        while offset:
            # 5000 overload some servers, but it is needed for sites like this with
            # no next links
            # http://www.memoryarchive.org/en/index.php?title=Special:Imagelist&sort=byname&limit=50&wpIlMatch=
            with requests.Session().post(
                url=self.config["index"],
                params={"title": "Special:Imagelist", "limit": limit, "offset": offset},
                timeout=30,
            ) as post_response:
                raw = post_response.text
            delay(self.config)
            # delicate wiki
            if re.search(
                r"(?i)(allowed memory size of \d+ bytes exhausted|Call to a member function getURL)",
                raw,
            ):
                if limit > 10:
                    print(
                        "Error: listing %d images in a chunk is not possible, trying tiny chunks"
                        % (limit)
                    )
                    limit = limit / 10
                    continue
                elif retries > 0:  # waste retries, then exit
                    retries -= 1
                    print("Retrying...")
                    continue
                else:
                    print("No more retries, exit...")
                    break

            raw = cleanHTML(raw)
            # archiveteam 1.15.1 <td class="TablePager_col_img_name"><a href="/index.php?title=File:Yahoovideo.jpg" title="File:Yahoovideo.jpg">Yahoovideo.jpg</a> (<a href="/images/2/2b/Yahoovideo.jpg">file</a>)</td>
            # wikanda 1.15.5 <td class="TablePager_col_img_user_text"><a
            # href="/w/index.php?title=Usuario:Fernandocg&amp;action=edit&amp;redlink=1"
            # class="new" title="Usuario:Fernandocg (página no
            # existe)">Fernandocg</a></td>
            r_images1 = r'(?im)<td class="TablePager_col_img_name"><a href[^>]+title="[^:>]+:(?P<filename>[^>]+)">[^<]+</a>[^<]+<a href="(?P<url>[^>]+/[^>/]+)">[^<]+</a>[^<]+</td>\s*<td class="TablePager_col_img_user_text"><a[^>]+>(?P<uploader>[^<]+)</a></td>'
            # wikijuegos 1.9.5
            # http://softwarelibre.uca.es/wikijuegos/Especial:Imagelist old
            # mediawiki version
            r_images2 = r'(?im)<td class="TablePager_col_links"><a href[^>]+title="[^:>]+:(?P<filename>[^>]+)">[^<]+</a>[^<]+<a href="(?P<url>[^>]+/[^>/]+)">[^<]+</a></td>\s*<td class="TablePager_col_img_timestamp">[^<]+</td>\s*<td class="TablePager_col_img_name">[^<]+</td>\s*<td class="TablePager_col_img_user_text"><a[^>]+>(?P<uploader>[^<]+)</a></td>'
            # gentoowiki 1.18
            r_images3 = r'(?im)<td class="TablePager_col_img_name"><a[^>]+title="[^:>]+:(?P<filename>[^>]+)">[^<]+</a>[^<]+<a href="(?P<url>[^>]+)">[^<]+</a>[^<]+</td><td class="TablePager_col_thumb"><a[^>]+><img[^>]+></a></td><td class="TablePager_col_img_size">[^<]+</td><td class="TablePager_col_img_user_text"><a[^>]+>(?P<uploader>[^<]+)</a></td>'
            # http://www.memoryarchive.org/en/index.php?title=Special:Imagelist&sort=byname&limit=50&wpIlMatch=
            # (<a href="/en/Image:109_0923.JPG" title="Image:109 0923.JPG">desc</a>) <a href="/en/upload/c/cd/109_0923.JPG">109 0923.JPG</a> . . 885,713 bytes . . <a href="/en/User:Bfalconer" title="User:Bfalconer">Bfalconer</a> . . 18:44, 17 November 2005<br />
            r_images4 = '(?im)<a href=[^>]+ title="[^:>]+:(?P<filename>[^>]+)">[^<]+</a>[^<]+<a href="(?P<url>[^>]+)">[^<]+</a>[^<]+<a[^>]+>(?P<uploader>[^<]+)</a>'
            r_images5 = (
                r'(?im)<td class="TablePager_col_img_name">\s*<a href[^>]*?>(?P<filename>[^>]+)</a>\s*\(<a href="(?P<url>[^>]+)">[^<]*?</a>\s*\)\s*</td>\s*'
                r'<td class="TablePager_col_thumb">[^\n\r]*?</td>\s*'
                r'<td class="TablePager_col_img_size">[^<]*?</td>\s*'
                r'<td class="TablePager_col_img_user_text">\s*(<a href="[^>]*?" title="[^>]*?">)?(?P<uploader>[^<]+?)(</a>)?\s*</td>'
            )

            # Select the regexp that returns more results
            regexps = [r_images1, r_images2, r_images3, r_images4, r_images5]
            count = 0
            i = 0
            regexp_best = 0
            for regexp in regexps:
                if len(re.findall(regexp, raw)) > count:
                    count = len(re.findall(regexp, raw))
                    regexp_best = i
                i += 1
            match = re.compile(regexps[regexp_best]).finditer(raw)

            # Iter the image results
            for i in match:
                url = i.group("url")
                url = Image.curateImageURL(self.config, url=url)
                filename = re.sub("_", " ", i.group("filename"))
                filename = undoHTMLEntities(text=filename)
                filename = unquote(filename)
                uploader = re.sub("_", " ", i.group("uploader"))
                uploader = undoHTMLEntities(text=uploader)
                uploader = unquote(uploader)
                images.append([filename, url, uploader])
                # print (filename, url)

            if re.search(r_next, raw):
                new_offset = re.findall(r_next, raw)[0]
                # Avoid infinite loop
                if new_offset != offset:
                    offset = new_offset
                    retries += 5  # add more retries if we got a page with offset
                else:
                    offset = ""
            else:
                offset = ""

        if len(images) == 1:
            print("    Found 1 image")
        else:
            print("    Found %d images" % (len(images)))

        images.sort()
        return images

    def getImageNamesAPI(self):
        """Retrieve file list: filename, url, uploader"""
        oldAPI = False
        aifrom = "!"
        images = []
        while aifrom:
            sys.stderr.write(".")  # progress
            params = {
                "action": "query",
                "list": "allimages",
                "aiprop": "url|user",
                "aifrom": aifrom,
                "format": "json",
                "ailimit": 50,
            }
            # FIXME Handle HTTP Errors HERE
            with requests.Session().get(
                url=self.config["api"], params=params, timeout=30
            ) as get_response:
                handleStatusCode(get_response)
                json_images = get_response.json()
            delay(self.config)

            if "query" in json_images:
                aifrom = ""
                if (
                    "query-continue" in json_images
                    and "allimages" in json_images["query-continue"]
                ):
                    if "aicontinue" in json_images["query-continue"]["allimages"]:
                        aifrom = json_images["query-continue"]["allimages"][
                            "aicontinue"
                        ]
                    elif "aifrom" in json_images["query-continue"]["allimages"]:
                        aifrom = json_images["query-continue"]["allimages"]["aifrom"]
                elif "continue" in json_images:
                    if "aicontinue" in json_images["continue"]:
                        aifrom = json_images["continue"]["aicontinue"]
                    elif "aifrom" in json_images["continue"]:
                        aifrom = json_images["continue"]["aifrom"]
                # print (aifrom)

                for image in json_images["query"]["allimages"]:
                    url = image["url"]
                    url = Image.curateImageURL(self.config, url=url)
                    # encoding to ascii is needed to work around this horrible bug:
                    # http://bugs.python.org/issue8136
                    # (ascii encoding removed because of the following)
                    #
                    # unquote() no longer supports bytes-like strings
                    # so unicode may require the following workaround:
                    # https://izziswift.com/how-to-unquote-a-urlencoded-unicode-string-in-python/
                    if "api" in self.config and (
                        ".wikia." in self.config["api"]
                        or ".fandom.com" in self.config["api"]
                    ):
                        filename = unquote(re.sub("_", " ", url.split("/")[-3]))
                    else:
                        filename = unquote(re.sub("_", " ", url.split("/")[-1]))
                    if u"%u" in filename:
                        raise NotImplementedError(
                            "Filename "
                            + filename
                            + " contains unicode. Please file an issue with WikiTeam."
                        )
                    uploader = re.sub("_", " ", image["user"])
                    images.append([filename, url, uploader])
            else:
                oldAPI = True
                break

        if oldAPI:
            gapfrom = "!"
            images = []
            while gapfrom:
                sys.stderr.write(".")  # progress
                # Some old APIs doesn't have allimages query
                # In this case use allpages (in nm=6) as generator for imageinfo
                # Example:
                # http://minlingo.wiki-site.com/api.php?action=query&generator=allpages&gapnamespace=6
                # &gaplimit=500&prop=imageinfo&iiprop=user|url&gapfrom=!
                params = {
                    "action": "query",
                    "generator": "allpages",
                    "gapnamespace": 6,
                    "gaplimit": 50,
                    "gapfrom": gapfrom,
                    "prop": "imageinfo",
                    "iiprop": "user|url",
                    "format": "json",
                }
                # FIXME Handle HTTP Errors HERE
                with requests.Session().get(
                    url=self.config["api"], params=params, timeout=30
                ) as get_response:
                    handleStatusCode(get_response)
                    json_images = get_response.json()
                delay(self.config)

                if "query" in json_images:
                    gapfrom = ""
                    if (
                        "query-continue" in json_images
                        and "allpages" in json_images["query-continue"]
                    ):
                        if "gapfrom" in json_images["query-continue"]["allpages"]:
                            gapfrom = json_images["query-continue"]["allpages"][
                                "gapfrom"
                            ]
                    # print (gapfrom)
                    # print (json_images['query'])

                    for image, props in json_images["query"]["pages"].items():
                        url = props["imageinfo"][0]["url"]
                        url = Image.curateImageURL(self.config, url=url)

                        tmp_filename = ":".join(props["title"].split(":")[1:])

                        filename = re.sub("_", " ", tmp_filename)
                        uploader = re.sub("_", " ", props["imageinfo"][0]["user"])
                        images.append([filename, url, uploader])
                    else:
                        # if the API doesn't return query data, then we're done
                        break

        if len(images) == 1:
            print("    Found 1 image")
        else:
            print("    Found %d images" % (len(images)))

        return images

    def saveImageNames(self, images: dict):
        """Save image list in a file, including filename, url and uploader"""

        imagesfilename = "%s-%s-images.txt" % (
            Domain(self.config).to_prefix(),
            self.config["date"],
        )
        with open(
            "%s/%s" % (self.config["path"], imagesfilename), "w", encoding="utf-8"
        ) as imagesfile:
            imagesfile.write(
                (
                    "\n".join(
                        [
                            filename + "\t" + url + "\t" + uploader
                            for filename, url, uploader in images
                        ]
                    )
                )
            )
            imagesfile.write("\n--END--")

        print("Image filenames and URLs saved at...", imagesfilename)

    def curateImageURL(self, url=""):
        """Returns an absolute URL for an image, adding the domain if missing"""

        if "index" in self.config and self.config["index"]:
            # remove from :// (http or https) until the first / after domain
            domainalone = (
                self.config["index"].split("://")[0]
                + "://"
                + self.config["index"].split("://")[1].split("/")[0]
            )
        elif "api" in self.config and self.config["api"]:
            domainalone = (
                self.config["api"].split("://")[0]
                + "://"
                + self.config["api"].split("://")[1].split("/")[0]
            )
        else:
            print("ERROR: no index nor API")
            sys.exit()

        if url.startswith("//"):  # Orain wikifarm returns URLs starting with //
            url = u"%s:%s" % (domainalone.split("://")[0], url)
        # is it a relative URL?
        elif url[0] == "/" or (
            not url.startswith("http://") and not url.startswith("https://")
        ):
            if url[0] == "/":  # slash is added later
                url = url[1:]
            # concat http(s) + domain + relative url
            url = u"%s/%s" % (domainalone, url)
        url = undoHTMLEntities(text=url)
        # url = unquote(url) #do not use unquote with url, it break some
        # urls with odd chars
        url = re.sub(" ", "_", url)

        return url
