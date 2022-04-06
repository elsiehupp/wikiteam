import os
import re
import sys
from enum import Enum, auto
from typing import List
from urllib.parse import unquote

import requests
from delay import delay
from domain import Domain
from exceptions import PageMissingError

# from get_json import get_json
from handle_status_code import handle_status_code
from log_error import logerror
from page_xml import get_xml_page
from truncate import truncate_filename
from util import clean_html, undo_html_entities


class ImageInfo:

    original_filename: str
    unquoted_filename: str
    original_url: str
    redirected_url: str
    original_url_redirected: bool
    uploader: str

    def __init__(self, filename: str, url: str, uploader: str):
        self.original_filename = filename
        self.unquoted_filename = unquote(filename)
        self.original_url = url
        self.redirected_url = ""
        self.uploader = uploader

    def url(self):
        if self.redirected_url is not None:
            return self.redirected_url
        elif self.original_url is not None:
            return self.original_url
        else:
            try:
                raise ValueError("No URL defined for ImageInfo %s" % self.filename())
            except ValueError:
                raise ValueError("No URL defined for ImageInfo %s" % str(self))

    def filename(self):
        if self.unquoted_filename is not None:
            return self.unquoted_filename
        elif self.original_filename is not None:
            return self.unquoted_filename
        else:
            try:
                raise ValueError("No filename defined for ImageInfo %s" % self.url())
            except ValueError:
                raise ValueError("No filename defined for ImageInfo %s" % str(self))

    def __str__(self):
        return self.filename()

    def __lt__(self, other):
        return str(self) < str(other)


class ResponseType(Enum):
    TITLE_RESPONSE = auto()
    DATA_RESPONSE = auto()


class ImageDumper:

    api: str = ""
    config: dict
    current_only: bool = False
    image_info_list: List[ImageInfo] = []
    index: str = ""
    path_for_images: str
    retries: int = 5

    def __init__(self, config: dict):
        self.config = config
        try:
            self.api = config["api"]
            self.current_only = config["current-only"]
            self.index = config["api"]
            self.retries = config["retries"]
            self.path_for_images = "%s/images" % (config["path"])
        except KeyError as error:
            print(error)

        self.fetch_titles()

    def fetch_titles(self):
        """Get list of image names"""

        print("")
        print("Retrieving image filenames")
        if self.api != "":
            self.image_info_list = self.fetch_titles_api()
        elif self.index != "":
            self.image_info_list = self.fetch_titles_scraper()

        # images = list(set(images)) # it is a list of lists
        self.image_info_list.sort()

        print("%d image names loaded" % (len(self.image_info_list)))
        return

    def fetch_titles_scraper(self):
        """Retrieve file list: filename, url, uploader"""

        # (?<! http://docs.python.org/library/re.html
        r_next = r"(?<!&amp;dir=prev)&amp;offset=(?P<offset>\d+)&amp;"
        offset = "29990101000000"  # january 1, 2999
        limit = 5000
        retries = self.retries
        while offset:
            # 5000 overload some servers, but it is needed for sites like this with
            # no next links
            # http://www.memoryarchive.org/en/index.php?title=Special:Imagelist&sort=byname&limit=50&wpIlMatch=
            with requests.Session().post(
                url=self.index,
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

            raw = clean_html(raw)
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
                url = self.curate_image_url(url=url)
                filename = re.sub("_", " ", i.group("filename"))
                filename = undo_html_entities(text=filename)
                filename = unquote(filename)
                uploader = re.sub("_", " ", i.group("uploader"))
                uploader = undo_html_entities(text=uploader)
                uploader = unquote(uploader)
                self.image_info_list.append(
                    ImageInfo(filename=filename, url=url, uploader=uploader)
                )
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

        if len(self.image_info_list) == 1:
            print("    Found 1 image")
        else:
            print("    Found %d images" % (len(self.image_info_list)))

        self.image_info_list.sort()
        return self.image_info_list

    def fetch_titles_api(self):
        """Retrieve file list: filename, url, uploader"""
        oldAPI = False
        aifrom = "!"
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
                url=self.api, params=params, timeout=30
            ) as get_response:
                handle_status_code(get_response)
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
                    url = self.curate_image_url(url=url)
                    # encoding to ascii is needed to work around this horrible bug:
                    # http://bugs.python.org/issue8136
                    # (ascii encoding removed because of the following)
                    #
                    # unquote() no longer supports bytes-like strings
                    # so unicode may require the following workaround:
                    # https://izziswift.com/how-to-unquote-a-urlencoded-unicode-string-in-python/
                    if "api" in self.config and (
                        ".wikia." in self.api or ".fandom.com" in self.api
                    ):
                        filename = unquote(re.sub("_", " ", url.split("/")[-3]))
                    else:
                        filename = unquote(re.sub("_", " ", url.split("/")[-1]))
                    # if "%u" in filename:
                    #     raise NotImplementedError(
                    #         "Filename "
                    #         + filename
                    #         + " contains unicode. Please file an issue with WikiTeam."
                    #     )
                    uploader = re.sub("_", " ", image["user"])
                    self.image_info_list.append(
                        ImageInfo(filename=filename, url=url, uploader=uploader)
                    )
            else:
                oldAPI = True
                break

        if oldAPI:
            gapfrom = "!"
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
                    url=self.api, params=params, timeout=30
                ) as get_response:
                    handle_status_code(get_response)
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
                        url = self.curate_image_url(url=url)

                        tmp_filename = ":".join(props["title"].split(":")[1:])

                        filename = re.sub("_", " ", tmp_filename)
                        uploader = re.sub("_", " ", props["imageinfo"][0]["user"])
                        self.image_info_list.append(
                            ImageInfo(filename=filename, url=url, uploader=uploader)
                        )
                    else:
                        # if the API doesn't return query data, then we're done
                        break

        if len(self.image_info_list) == 1:
            print("    Found 1 image")
        else:
            print("    Found %d images" % (len(self.image_info_list)))

        return self.image_info_list

    def fetch_xml_description_for_title(self, title: str) -> str:
        """Get XML for image description page"""
        self.config["current-only"] = 1  # tricky to get only the most recent desc
        return "".join(
            [x for x in get_xml_page(config=self.config, title=title, verbose=False)]
        )

    def generate_dump(self, filename_limit: int = 100, start: str = ""):
        """Save files and descriptions using a file list"""

        if self.image_info_list is None:
            self.fetch_titles()

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
        for image_info in self.image_info_list:
            if image_info.filename == start:  # start downloading from start (included)
                lock = False
            if lock:
                continue
            delay(self.config)

            # saving file
            # truncate filename if length > 100 (100 + 32 (md5) = 132 < 143 (crash
            # limit). Later .desc is added to filename, so better 100 as max)
            image_info.unquoted_filename = unquote(image_info.filename())
            if len(image_info.unquoted_filename) > filename_limit:
                # split last . (extension) and then merge
                image_info.unquoted_filename = truncate_filename(
                    filename=image_info.unquoted_filename
                )
                print(
                    "Filename is too long, truncating. Now it is:",
                    image_info.unquoted_filename,
                )

            self.handle_response(image_info, ResponseType.DATA_RESPONSE)

            with requests.Session().head(
                url=image_info.url(), allow_redirects=True
            ) as header_response:
                image_info.original_url_redirected = len(header_response.history) > 0

                if image_info.original_url_redirected:
                    # print 'Site is redirecting us to: ', header_response.url
                    image_info.redirected_url = header_response.url

            self.handle_response(image_info, ResponseType.TITLE_RESPONSE)

            delay(self.config)
            count += 1
            if count % 10 == 0:
                print("")
                print("->  Downloaded %d images" % (count))

        print("")
        print("->  Downloaded %d images" % (count))

    def handle_response(self, image_info: ImageInfo, response_type: ResponseType):
        with requests.Session().get(
            url=image_info.url(), allow_redirects=False
        ) as get_response:
            # Try to fix a broken HTTP to HTTPS redirect
            if get_response.status_code == 404 and image_info.original_url_redirected:
                if (
                    image_info.original_url.split("://")[0] == "http"
                    and image_info.redirected_url.split("://")[0] == "https"
                ):
                    image_info.original_url = (
                        "https://" + image_info.original_url.split("://")[1]
                    )
                    # print 'Maybe a broken http to https redirect, trying ', url
                    with requests.Session().get(
                        url=image_info.original_url, allow_redirects=False
                    ) as second_get_response:
                        if second_get_response.status_code == 404:
                            logerror(
                                self.config,
                                text="File %s at URL %s is missing"
                                % (image_info.filename(), image_info.original_url),
                            )

                    if get_response.status_code == 404:
                        logerror(
                            self.config,
                            text="File %s at URL %s is missing"
                            % (image_info.filename(), image_info.url()),
                        )

            if response_type == ResponseType.TITLE_RESPONSE:
                self.save_description(filename=image_info.filename())
            elif response_type == ResponseType.DATA_RESPONSE:
                image_file_path = os.path.join(
                    self.path_for_images, image_info.filename()
                )
                try:
                    with open(image_file_path, "wb") as image_file:
                        image_file.write(get_response.content)
                except OSError:
                    logerror(
                        self.config,
                        text="File %s could not be created by OS" % (image_file_path),
                    )

    def save_description(self, filename: str):
        # saving description if any
        try:
            title = "Image:%s" % (filename)
            if self.config["revisions"] and self.api and self.api.endswith("api.php"):
                with requests.Session().get(
                    self.api + "?action=query&export&exportnowrap&titles=%s" % title
                ) as get_response:
                    xmlfiledesc = get_response.text
            else:
                xmlfiledesc = self.fetch_xml_description_for_title(
                    title=title
                )  # use ImageDumper: for backwards compatibility
        except PageMissingError:
            xmlfiledesc = ""
            logerror(
                self.config,
                text='The page "%s" was missing in the wiki (probably deleted)'
                % (str(title)),
            )

        try:
            with open(
                f"{self.path_for_images}/{filename}.desc", "w", encoding="utf-8"
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
                text="File %s/%s.desc could not be created by OS"
                % (self.path_for_images, filename),
            )

    def save_image_names(self):
        """Save image list in a file, including filename, url and uploader"""

        if self.image_info_list is None:
            self.fetch_titles()

        imagesfilename = "{}-{}-images.txt".format(
            Domain(self.config).to_prefix(),
            self.config["date"],
        )
        with open(
            "{}/{}".format(self.config["path"], imagesfilename), "w", encoding="utf-8"
        ) as imagesfile:
            imagesfile.write(
                "\n".join(
                    [
                        image_info.filename
                        + "\t"
                        + image_info.url()
                        + "\t"
                        + image_info.uploader
                        for image_info in self.image_info_list
                    ]
                )
            )
            imagesfile.write("\n--END--")

        print("Image filenames and URLs saved at...", imagesfilename)

    def curate_image_url(self, url=""):
        """Returns an absolute URL for an image, adding the domain if missing"""

        if self.index != "":
            # remove from :// (http or https) until the first / after domain
            domainalone = (
                self.index.split("://")[0]
                + "://"
                + self.index.split("://")[1].split("/")[0]
            )
        elif "api" in self.config and self.api:
            domainalone = (
                self.api.split("://")[0]
                + "://"
                + self.api.split("://")[1].split("/")[0]
            )
        else:
            print("ERROR: no index nor API")
            sys.exit()

        if url.startswith("//"):  # Orain wikifarm returns URLs starting with //
            url = "{}:{}".format(domainalone.split("://")[0], url)
        # is it a relative URL?
        elif url[0] == "/" or (
            not url.startswith("http://") and not url.startswith("https://")
        ):
            if url[0] == "/":  # slash is added later
                url = url[1:]
            # concat http(s) + domain + relative url
            url = f"{domainalone}/{url}"
        url = undo_html_entities(text=url)
        # url = unquote(url) #do not use unquote with url, it break some
        # urls with odd chars
        url = re.sub(" ", "_", url)

        return url
