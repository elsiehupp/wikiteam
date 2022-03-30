import argparse
import datetime
import http
import os
import re
import requests
import sys

from .api_info import ApiInfo
from .domain import Domain
from .index_check import checkIndex
from .user_agent import UserAgent
from .version import getVersion
from .wiki_check import getWikiEngine


def getParameters(params=[]):
    if not params:
        params = sys.argv

    parser = argparse.ArgumentParser(description="")

    # General params
    parser.add_argument("-v", "--version", action="version", version=getVersion())

    # URL params
    groupWikiOrAPIOrIndex = parser.add_argument_group(
        "Starting download URL (one of these is required)"
    )
    groupWikiOrAPIOrIndex.add_argument(
        "--wiki-url",
        dest="wiki",
        metavar="http://wiki.example.org",
        default="",
        nargs="?",
        help="URL to wiki",
    )
    groupWikiOrAPIOrIndex.add_argument(
        "--api-url",
        dest="api",
        metavar="[http://wiki.example.org/w/api.php]",
        help="URL to api.php",
    )
    groupWikiOrAPIOrIndex.add_argument(
        "--index-url",
        dest="index",
        metavar="[http://wiki.example.org/w/index.php]",
        help="URL to index.php",
    )

    outputVariables = parser.add_argument_group("Output variables")
    outputVariables.add_argument(
        "-o",
        "--output",
        metavar="[~/Downloads]",
        help="directory where you'd like to store the dump"
        "(defaults to working directory)",
    )
    outputVariables.add_argument(
        "--resume",
        action="store_true",
        help="resume a previous incomplete dump\n"
        "(you must use the same output directory as before)",
    )

    # parser.add_argument("--force", action="store_true", help="")

    groupAuthVariables = parser.add_argument_group("Authentication variables")
    groupAuthVariables.add_argument(
        "--user",
        metavar="[admin]",
        dest="user",
        help="username if authentication is required",
    )
    groupAuthVariables.add_argument(
        "--pass",
        metavar="[alpine]",
        dest="password",
        help="password if authentication is required",
    )
    groupAuthVariables.add_argument(
        "--cookies", metavar="[./cookies.txt]", help="path to a cookies.txt file"
    )

    timeoutVariables = parser.add_argument_group("Variables for avoiding API limits")
    timeoutVariables.add_argument(
        "--delay",
        metavar="[0.5]",
        default=0,
        type=float,
        help="adds a delay (in seconds) between calls",
    )
    timeoutVariables.add_argument(
        "--retries",
        metavar="[5]",
        default=5,
        help="maximum number of automatic retries before aborting",
    )

    # Download params
    groupDownload = parser.add_argument_group(
        "Data and format (what to download from the wiki)"
    )
    groupDownload.add_argument(
        "--xml",
        action="store_true",
        help="generates a full history XML dump\n"
        "(--xml --current-only for current revisions only)",
    )
    groupDownload.add_argument(
        "--current-only",
        dest="currentonly",
        action="store_true",
        help="store only the current version of pages",
    )
    groupDownload.add_argument(
        "--revisions",
        dest="revisions",
        action="store_true",
        help="download all revisions from an API generator\n"
        "(works on MediaWiki 1.27+ only)",
    )
    groupDownload.add_argument(
        "--images", action="store_true", help="generates an image dump"
    )
    groupDownload.add_argument(
        "--namespaces",
        metavar="[1,2,3]",
        help="comma-separated list of namespaces to include\n"
        "(by default all namespaces are downloaded)",
    )
    groupDownload.add_argument(
        "--exnamespaces",
        metavar="[1,2,3]",
        help="comma-separated list of namespaces to exclude",
    )

    # Meta info params
    groupMeta = parser.add_argument_group("Bulk download variables")
    groupMeta.add_argument(
        "--get-wiki-engine", action="store_true", help="returns the wiki engine"
    )
    groupMeta.add_argument(
        "--fail-fast",
        dest="failfast",
        action="store_true",
        help="avoid resuming and discard failing wikis quickly",
    )

    args = parser.parse_args()
    # print (args)

    # Don't mix download params and meta info params
    if (args.xml or args.images) and (args.get_wiki_engine):
        print("ERROR: Don't mix download params and meta info params")
        parser.print_help()
        sys.exit(1)

    # No download params and no meta info params? Exit
    if (not args.xml and not args.images) and (not args.get_wiki_engine):
        print("ERROR: Use at least one download param or meta info param")
        parser.print_help()
        sys.exit(1)

    # Execute meta info params
    if args.wiki:
        if args.get_wiki_engine:
            print(getWikiEngine(url=args.wiki))
            sys.exit()

    # Create requests.Session()
    cookie_jar = http.cookiejar.MozillaCookieJar()
    if args.cookies:
        cookie_jar.load(args.cookies)
        print("")
        print("Using cookies from %s" % args.cookies)

    with requests.Session():
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            # Courtesy datashaman https://stackoverflow.com/a/35504626
            __retries__ = Retry(
                total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504]
            )
            requests.Session().mount("https://", HTTPAdapter(max_retries=__retries__))
            requests.Session().mount("http://", HTTPAdapter(max_retries=__retries__))
        except Exception:
            # Our urllib3/requests is too old
            pass
        requests.Session().cookies = cookie_jar
        requests.Session().headers.update({"User-Agent": str(UserAgent())})
        if args.user and args.password:
            requests.Session().auth = (args.user, args.password)

        # check URLs
        for url in [args.api, args.index, args.wiki]:
            if url and (
                not url.startswith("http://") and not url.startswith("https://")
            ):
                print(url)
                print("ERROR: URLs must start with http:// or https://\n")
                parser.print_help()
                sys.exit(1)

        # Get API and index and verify
        api = args.api and args.api or ""
        index = args.index and args.index or ""
        if api == "" or index == "":
            if args.wiki:
                if getWikiEngine(args.wiki) == "MediaWiki":
                    api_info = ApiInfo(args.wiki)
                    api2 = api_info.api_string
                    index_from_api = api_info.index_php_url
                    if not api:
                        api = api2
                    if not index:
                        index = index_from_api
                else:
                    print(
                        "ERROR: Unsupported wiki. Wiki engines supported are: MediaWiki"
                    )
                    sys.exit(1)
            else:
                if api == "":
                    pass
                elif index == "":
                    index = "/".join(api.split("/")[:-1]) + "/index.php"

        index_from_api: str

        if api:
            api_info = ApiInfo(api)
            check = api_info.checkRetryAPI(
                retries=int(args.retries),
                api_client=args.revisions,
            )
            checkedapi = api_info.api_string

        if api and check:
            # Replace the index URL we got from the API check
            index_from_api = api_info.index_php_url
            api = checkedapi
            print("API is OK: " + checkedapi)
        else:
            if index and not args.wiki:
                print("API not available. Trying with index.php only.")
                args.api = None
            else:
                print("Error in API. Please, provide a correct path to API")
                sys.exit(1)

        if index and checkIndex(index_php_url=index, cookies_file_path=args.cookies):
            print("index.php is OK")
        else:
            index = index_from_api
            if index and index.startswith("//"):
                index = args.wiki.split("//")[0] + index
            if index and checkIndex(
                index_php_url=index, cookies_file_path=args.cookies
            ):
                print("index.php is OK")
            else:
                try:
                    index = "/".join(index.split("/")[:-1])
                except AttributeError:
                    index = None
                if index and checkIndex(
                    index_php_url=index, cookies_file_path=args.cookies
                ):
                    print("index.php is OK")
                else:
                    print("Error in index.php.")
                    if not args.revisions:
                        print(
                            "Please, provide a correct path to index.php or use --revisions. Terminating."
                        )
                        sys.exit(1)

        # check user and pass (one requires both)
        if (args.user and not args.password) or (args.password and not args.user):
            print("ERROR: Both --user and --pass are required for authentication.")
            parser.print_help()
            sys.exit(1)

        namespace_list = ["all"]
        exnamespaces = []
        # Process namespace inclusions
        if args.namespaces:
            # fix, why - ?  and... --namespaces= all with a space works?
            if (
                re.search(r"[^\d, \-]", args.namespaces)
                and args.namespaces.lower() != "all"
            ):
                print(
                    "Invalid namespace values.\nValid format is integer(s) separated by commas"
                )
                sys.exit()
            else:
                ns = re.sub(" ", "", args.namespaces)
                if ns.lower() == "all":
                    namespace_list = ["all"]
                else:
                    namespace_list = [int(i) for i in ns.split(",")]

        # Process namespace exclusions
        if args.exnamespaces:
            if re.search(r"[^\d, \-]", args.exnamespaces):
                print(
                    "Invalid namespace values.\nValid format is integer(s) separated by commas"
                )
                sys.exit(1)
            else:
                ns = re.sub(" ", "", args.exnamespaces)
                if ns.lower() == "all":
                    print("You cannot exclude all namespaces.")
                    sys.exit(1)
                else:
                    exnamespaces = [int(i) for i in ns.split(",")]

        # --current-only requires --xml
        if args.currentonly and not args.xml:
            print("--current-only requires --xml\n")
            parser.print_help()
            sys.exit(1)

        config = {
            "current-only": args.currentonly,
            "date": datetime.datetime.now().strftime("%Y%m%d"),
            "api": api,
            "failfast": args.failfast,
            "http_method": "POST",
            "index": index,
            "images": args.images,
            "logs": False,
            "xml": args.xml,
            "revisions": args.revisions,
            "namespaces": namespace_list,
            "exnamespaces": exnamespaces,
            "path": args.output and os.path.normpath(args.output) or "",
            "cookies": args.cookies or "",
            "delay": args.delay,
            "retries": int(args.retries),
        }

        other = {
            "resume": args.resume,
            "filenamelimit": 100,  # do not change
            # "force": args.force,
            "requests.Session()": requests.Session(),
        }

        # calculating path, if not defined by user with --path=
        if not config["path"]:
            config["path"] = "./%s-%s-wikidump" % (
                Domain(config).to_prefix(),
                config["date"],
            )
            print("")
            print("No --path argument provided. Defaulting to:")
            print("  [working_directory]/[domain_prefix]-[date]-wikidump")
            print("Which expands to:")
            print("  " + config["path"])

        return config, other
