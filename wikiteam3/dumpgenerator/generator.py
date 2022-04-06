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

from cli import get_parameters
from config import load_config, save_config
from domain import Domain
from greeter import bye, print_welcome
from image import ImageDumper
from index_php import save_index_php
from logs import save_logs
from page_special_version import save_special_version
from page_titles import fetch_page_titles, read_titles
from site_info import save_site_info
from truncate import truncate_filename
from util import undo_html_entities
from wiki_avoid import avoid_wikimedia_projects
from xml_dump import generate_xml_dump
from xml_integrity import check_xml_integrity


class DumpGenerator:
    def __init__(params=[]):
        """Main function"""
        config_filename = "config.json"
        config, other = get_parameters(params)
        avoid_wikimedia_projects(config, other)

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
                if not os.path.isfile("{}/{}".format(config["path"], config_filename)):
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
            config = load_config(config, config_filename=config_filename)
        else:
            os.mkdir(config["path"])
            save_config(config, config_filename=config_filename)

        if other["resume"]:
            DumpGenerator.resume_previous_dump(config, other)
        else:
            DumpGenerator.create_new_nump(config, other)

        save_index_php(config)
        save_special_version(config)
        save_site_info(config)
        bye()

    @staticmethod
    def create_new_nump(config: dict, other={}):
        print("Trying generating a new dump into a new directory...")
        print("")
        if config["xml"]:
            fetch_page_titles(config)
            titles = read_titles(config)
            generate_xml_dump(config, titles=titles)
            check_xml_integrity(config, titles=titles)
        if config["images"]:
            image_dump = ImageDumper(config)
            image_dump.save_image_names()
            image_dump.generate_dump(other)
        if config["logs"]:
            save_logs(config)

    @staticmethod
    def resume_previous_dump(config: dict, other={}, filename_limit: int = 100):
        images = []
        print("Resuming previous dump process...")
        if config["xml"]:
            titles = read_titles(config)
            try:
                with FileReadBackwards(
                    "%s/%s-%s-titles.txt"
                    % (
                        config["path"],
                        Domain(config).to_prefix(),
                        config["date"],
                    ),
                    encoding="utf-8",
                ) as file_read_backwards:
                    last_title = file_read_backwards.readline().strip()
                    if last_title == "":
                        last_title = file_read_backwards.readline().strip()
            except Exception:
                last_title = ""  # probably file does not exists
            if last_title == "--END--":
                # titles list is complete
                print("Title list was completed in the previous session")
            else:
                print("Title list is incomplete. Reloading...")
                # do not resume, reload, to avoid inconsistences, deleted pages or
                # so
                fetch_page_titles(config)

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
                ) as file_read_backwards:
                    for line in file_read_backwards:
                        if line.strip() == "</mediawiki>":
                            # xml dump is complete
                            xmliscomplete = True
                            break

                        xmltitle = re.search(r"<title>([^<]+)</title>", line)
                        if xmltitle:
                            lastxmltitle = undo_html_entities(text=xmltitle.group(1))
                            break
            except Exception:
                pass  # probably file does not exists

            if xmliscomplete:
                print("XML dump was completed in the previous session")
            elif lastxmltitle:
                # resuming...
                print('Resuming XML dump from "%s"' % (lastxmltitle))
                titles = read_titles(config, start=lastxmltitle)
                generate_xml_dump(config, titles=titles, start=lastxmltitle)
            else:
                # corrupt? only has XML header?
                print("XML is corrupt? Regenerating...")
                titles = read_titles(config)
                generate_xml_dump(config, titles=titles)

        if config["images"]:
            # load images
            lastimage = ""
            try:
                with open(
                    "%s/%s-%s-images.txt"
                    % (config["path"], Domain(config).to_prefix(), config["date"]),
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
            if lastimage == "--END--":
                print("Image list was completed in the previous session")
            else:
                print("Image list is incomplete. Reloading...")
                # do not resume, reload, to avoid inconsistences, deleted images or
                # so
                image_dumper = ImageDumper(config)
                image_dumper.fetch_titles()
                image_dumper.save_image_names()
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
                if len(filename2) > filename_limit:
                    filename2 = truncate_filename(
                        filename=filename2, filename_limit=filename_limit
                    )
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
                ImageDumper(config).generate_dump(
                    filename_limit=filename_limit, start=lastfilename2
                )

        if config["logs"]:
            # fix
            pass
