try:
    import os
    import re
    import sys
    from file_read_backwards import FileReadBackwards


except ImportError:
    print(
        """
        Please install poetry with:
            $ pip install poetry.
        Then rerun py with:
            $ poetry run python py
    """
    )
    sys.exit(1)

from .util import undoHTMLEntities
from .cli import getParameters
from .config import loadConfig, saveConfig
from .domain import Domain
from .image import Image
from .index_php import saveIndexPHP
from .logs import saveLogs
from .page_special_version import saveSpecialVersion
from .page_titles import fetchPageTitles, readTitles
from .site_info import saveSiteInfo
from .truncate import truncateFilename
from .wiki_avoid import avoidWikimediaProjects
from .greeter import print_welcome, bye
from .xml_dump import generateXMLDump
from .xml_integrity import checkXMLIntegrity


class DumpGenerator:
    def __init__(params=[]):
        """Main function"""
        config_filename = "config.json"
        config, other = getParameters(params)
        avoidWikimediaProjects(config, other)

        print_welcome()
        print("Analysing %s" % (config["api"] and config["api"] or config["index"]))

        # creating path or resuming if desired
        c = 2
        # to avoid concat blabla-2, blabla-2-3, and so on...
        originalpath = config["path"]
        # do not enter if resume is requested from begining
        while not other["resume"] and os.path.isdir(config["path"]):
            print('\nWarning!: "%s" path exists' % (config["path"]))
            reply = ""
            # if config["failfast"]:
            #     retry = "yes"
            while reply.lower() not in ["yes", "y", "no", "n"]:
                reply = input(
                    'There is a dump in "%s", probably incomplete.\nIf you choose resume, to avoid conflicts, the parameters you have chosen in the current requests.Session() will be ignored\nand the parameters available in "%s/%s" will be loaded.\nDo you want to resume ([yes, y], [no, n])? '
                    % (config["path"], config["path"], config_filename)
                )
            if reply.lower() in ["yes", "y"]:
                if not os.path.isfile("%s/%s" % (config["path"], config_filename)):
                    print("No config file found. I can't resume. Aborting.")
                    sys.exit()
                print("You have selected: YES")
                other["resume"] = True
                break
            elif reply.lower() in ["no", "n"]:
                print("You have selected: NO")
                other["resume"] = False
            config["path"] = "%s-%d" % (originalpath, c)
            print('Trying to use path "%s"...' % (config["path"]))
            c += 1

        if other["resume"]:
            print("Loading config file...")
            config = loadConfig(config, config_filename=config_filename)
        else:
            os.mkdir(config["path"])
            saveConfig(config, config_filename=config_filename)

        if other["resume"]:
            DumpGenerator.resumePreviousDump(config, other)
        else:
            DumpGenerator.createNewDump(config, other)

        saveIndexPHP(config)
        saveSpecialVersion(config)
        saveSiteInfo(config)
        bye()

    def createNewDump(config: dict, other={}):
        images = []
        print("Trying generating a new dump into a new directory...")
        print("")
        if config["xml"]:
            fetchPageTitles(config)
            titles = readTitles(config)
            generateXMLDump(config, titles=titles)
            checkXMLIntegrity(config, titles=titles)
        if config["images"]:
            images += Image.getImageNames(config)
            Image.saveImageNames(config, images)
            Image.generateImageDump(config, other, images)
        if config["logs"]:
            saveLogs(config)

    def resumePreviousDump(config: dict, other={}):
        images = []
        print("Resuming previous dump process...")
        if config["xml"]:
            titles = readTitles(config)
            try:
                with FileReadBackwards(
                    "%s/%s-%s-titles.txt"
                    % (
                        config["path"],
                        Domain(config).to_prefix(),
                        config["date"],
                    ),
                    encoding="utf-8",
                ) as frb:
                    lasttitle = frb.readline().strip()
                    if lasttitle == "":
                        lasttitle = frb.readline().strip()
            except Exception:
                lasttitle = ""  # probably file does not exists
            if lasttitle == "--END--":
                # titles list is complete
                print("Title list was completed in the previous session")
            else:
                print("Title list is incomplete. Reloading...")
                # do not resume, reload, to avoid inconsistences, deleted pages or
                # so
                fetchPageTitles(config)

            # checking xml dump
            xmliscomplete = False
            lastxmltitle = None
            try:
                with FileReadBackwards(
                    "%s/%s-%s-%s.xml"
                    % (
                        config["path"],
                        Domain(config).to_prefix(),
                        config["date"],
                        config["current-only"] and "current-only" or "history",
                    ),
                    encoding="utf-8",
                ) as frb:
                    for l in frb:
                        if l.strip() == "</mediawiki>":
                            # xml dump is complete
                            xmliscomplete = True
                            break

                        xmltitle = re.search(r"<title>([^<]+)</title>", l)
                        if xmltitle:
                            lastxmltitle = undoHTMLEntities(text=xmltitle.group(1))
                            break
            except Exception:
                pass  # probably file does not exists

            if xmliscomplete:
                print("XML dump was completed in the previous session")
            elif lastxmltitle:
                # resuming...
                print('Resuming XML dump from "%s"' % (lastxmltitle))
                titles = readTitles(config, start=lastxmltitle)
                generateXMLDump(config, titles=titles, start=lastxmltitle)
            else:
                # corrupt? only has XML header?
                print("XML is corrupt? Regenerating...")
                titles = readTitles(config)
                generateXMLDump(config, titles=titles)

        if config["images"]:
            # load images
            lastimage = ""
            try:
                with open(
                    "%s/%s-%s-images.txt"
                    % (config["path"], Domain(config).to_prefix(), config["date"]),
                    "r",
                    encoding="utf-8",
                ) as images_list_file:
                    lines = images_list_file.readlines()
                    for line in lines:
                        if re.search(r"\t", line):
                            images.append(line.split("\t"))
                    lastimage = lines[-1].strip()
                    if lastimage == "":
                        lastimage = lines[-2].strip()
            except FileNotFoundError:
                pass  # probably file does not exists
            if lastimage == u"--END--":
                print("Image list was completed in the previous session")
            else:
                print("Image list is incomplete. Reloading...")
                # do not resume, reload, to avoid inconsistences, deleted images or
                # so
                images = Image.getImageNames(config)
                Image.saveImageNames(config, images)
            # checking images directory
            listdir = []
            try:
                listdir = os.listdir("%s/images" % (config["path"]))
            except OSError:
                pass  # probably directory does not exist
            listdir.sort()
            complete = True
            lastfilename = ""
            lastfilename2 = ""
            c = 0
            for filename, url, uploader in images:
                lastfilename2 = lastfilename
                # return always the complete filename, not the truncated
                lastfilename = filename
                filename2 = filename
                if len(filename2) > other["filenamelimit"]:
                    filename2 = truncateFilename(other, filename=filename2)
                if filename2 not in listdir:
                    complete = False
                    break
                c += 1
            print(
                "%d images were found in the directory from a previous requests.Session()"
                % (c)
            )
            if complete:
                # image dump is complete
                print("Image dump was completed in the previous session")
            else:
                # we resume from previous image, which may be corrupted (or missing
                # .desc)  by the previous requests.Session() ctrl-c or abort
                Image.generateImageDump(config, other, images, start=lastfilename2)

        if config["logs"]:
            # fix
            pass
