try:
    import contextlib
    import os
    import re
    import sys
    import traceback

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

from typing import Dict

from wikiteam3.dumpgenerator.cli.cli import get_parameters
from wikiteam3.dumpgenerator.cli.greeter import bye, welcome
from wikiteam3.dumpgenerator.config import Config, load_config, save_config
from wikiteam3.dumpgenerator.dump.image.image import Image
from wikiteam3.dumpgenerator.dump.misc.index_php import save_index_php
from wikiteam3.dumpgenerator.dump.misc.site_info import save_site_info
from wikiteam3.dumpgenerator.dump.misc.special_logs import save_logs
from wikiteam3.dumpgenerator.dump.misc.special_version import save_special_version
from wikiteam3.dumpgenerator.dump.xmldump.xml_dump import generate_xml_dump
from wikiteam3.dumpgenerator.dump.xmldump.xml_integrity import check_xml_integrity
from wikiteam3.dumpgenerator.log.log_error import do_log_error
from wikiteam3.utils import (
    avoid_wikimedia_projects,
    domain_2_prefix,
    undo_html_entities,
)


# From https://stackoverflow.com/a/57008707
class Tee:
    def __init__(self, filename):
        self.file = open(filename, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        if exc_type is not None:
            self.file.write(traceback.format_exc())
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()


class DumpGenerator:
    config_filename = "config.json"

    @staticmethod
    def __init__(params=None):
        """Main function"""
        config_filename = DumpGenerator.config_filename
        config, other = get_parameters(params=params)
        avoid_wikimedia_projects(config=config, other=other)

        with (
            Tee(other["stdout_log_path"])
            if other["stdout_log_path"] is not None
            else contextlib.nullcontext()
        ):
            print(welcome())
            print(f"Analysing {config.api if config.api else config.index}")

            # creating path or resuming if desired
            c = 2
            # to avoid concat blabla-2, blabla-2-3, and so on...
            originalpath = config.path
            # do not enter if resume is requested from begining
            while not other["resume"] and os.path.isdir(config.path):
                print('\nWarning!: "%s" path exists' % (config.path))
                reply = ""
                if config.failfast:
                    reply = "yes"
                while reply.lower() not in ["yes", "y", "no", "n"]:
                    reply = input(
                        'There is a dump in "%s", probably incomplete.\nIf you choose resume, to avoid conflicts, the parameters you have chosen in the current session will be ignored\nand the parameters available in "%s/%s" will be loaded.\nDo you want to resume ([yes, y], [no, n])? '
                        % (config.path, config.path, config_filename)
                    )
                if reply.lower() in ["yes", "y"]:
                    if not os.path.isfile(f"{config.path}/{config_filename}"):
                        print("No config file found. I can't resume. Aborting.")
                        sys.exit()
                    print("You have selected: YES")
                    other["resume"] = True
                    break
                elif reply.lower() in ["no", "n"]:
                    print("You have selected: NO")
                    other["resume"] = False
                config.path = "%s-%d" % (originalpath, c)
                print(f'Trying to use path "{config.path}"...')
                c += 1

            if other["resume"]:
                print("Loading config file...")
                config = load_config(config=config, config_filename=config_filename)
            else:
                os.mkdir(config.path)
                save_config(config=config, config_filename=config_filename)

            if other["resume"]:
                DumpGenerator.resume_previous_dump(config=config, other=other)
            else:
                DumpGenerator.create_new_dump(config=config, other=other)

            save_index_php(config=config, session=other["session"])
            save_special_version(config=config, session=other["session"])
            save_site_info(config=config, session=other["session"])
            bye()

    @staticmethod
    def create_new_dump(config: Config, other: Dict):
        # we do lazy title dumping here :)
        images = []
        print("Trying generating a new dump into a new directory...")
        if config.xml:
            generate_xml_dump(config=config, resume=False, session=other["session"])
            check_xml_integrity(config=config)
        if config.images:
            images += Image.get_image_names(config=config, session=other["session"])
            Image.save_image_names(
                config=config, images=images, session=other["session"]
            )
            Image.generate_image_dump(
                config=config, other=other, images=images, session=other["session"]
            )
        if config.logs:
            save_logs(config=config)

    @staticmethod
    def resume_previous_dump(config: Config, other: Dict):
        images = []
        print("Resuming previous dump process...")
        if config.xml:
            # checking xml dump
            xmliscomplete = False
            lastxmltitle = None
            lastxmlrevid = None
            try:
                with FileReadBackwards(
                    "%s/%s-%s-%s.xml"
                    % (
                        config.path,
                        domain_2_prefix(config=config),
                        config.date,
                        "current" if config.curonly else "history",
                    ),
                    encoding="utf-8",
                ) as frb:
                    for l in frb:
                        if l.strip() == "</mediawiki>":
                            # xml dump is complete
                            xmliscomplete = True
                            break

                        if xmlrevid := re.search(r"    <id>([^<]+)</id>", l):
                            lastxmlrevid = int(xmlrevid.group(1))
                        if xmltitle := re.search(r"<title>([^<]+)</title>", l):
                            lastxmltitle = undo_html_entities(text=xmltitle.group(1))
                            break

            except Exception:
                pass  # probably file does not exists

            if xmliscomplete:
                print("XML dump was completed in the previous session")
            elif lastxmltitle:
                # resuming...
                print(
                    f'Resuming XML dump from "{lastxmltitle}" (revision id {lastxmlrevid})'
                )
                generate_xml_dump(
                    config=config,
                    session=other["session"],
                    resume=True,
                )
            else:
                # corrupt? only has XML header?
                print("XML is corrupt? Regenerating...")
                generate_xml_dump(config=config, resume=False, session=other["session"])

        if config.images:
            # load images list
            lastimage = ""
            images_file_path = "{}/{}-{}-images.txt".format(
                config.path,
                domain_2_prefix(config=config),
                config.date,
            )
            if os.path.exists(images_file_path):
                with open(images_file_path) as f:
                    lines = f.read().splitlines()
                    images.extend(l.split("\t") for l in lines if re.search(r"\t", l))
                    if len(lines) == 0:  # empty file
                        lastimage = "--EMPTY--"
                    if not lastimage:
                        lastimage = lines[-1].strip()
                    if lastimage == "":
                        lastimage = lines[-2].strip()
            if images and len(images[0]) < 5:
                print(
                    "Warning: Detected old images list (images.txt) format.\n"
                    + "You can delete 'images.txt' manually and restart the script."
                )
                sys.exit(1)
            if lastimage == "--END--":
                print("Image list was completed in the previous session")
            else:
                print("Image list is incomplete. Reloading...")
                # do not resume, reload, to avoid inconsistences, deleted images or
                # so
                images = Image.get_image_names(config=config, session=other["session"])
                Image.save_image_names(
                    config=config, images=images, session=other["session"]
                )
            # checking images directory
            listdir = []
            try:
                listdir = os.listdir(f"{config.path}/images")
            except OSError:
                pass  # probably directory does not exist
            listdir = set(listdir)
            c_desc = 0
            c_images = 0
            c_checked = 0
            for filename, url, uploader, size, sha1 in images:
                # lastfilename = filename
                if other["filenamelimit"] < len(filename.encode("utf-8")):
                    do_log_error(
                        config=config,
                        to_stdout=True,
                        text=f"Filename too long(>240 bytes), skipping: {filename}",
                    )
                    continue
                if filename in listdir:
                    c_images += 1
                if f"{filename}.desc" in listdir:
                    c_desc += 1
                c_checked += 1
                if c_checked % 100000 == 0:
                    print(f"checked {c_checked}/{len(images)} records", end="\r")
            print(
                f"{len(images)} records in images.txt, {c_images} images and {c_desc} .desc were saved in the previous session"
            )
            if c_desc < len(images):
                complete = False
            elif c_images < len(images):
                complete = False
                print(
                    "WARNING: Some images were not saved. You may want to delete their \n"
                    + ".desc files and re-run the script to redownload the missing images.\n"
                    + "(If images URL are unavailable, you can ignore this warning.)\n"
                    + "(In most cases, if the number of .desc files equals the number of \n"
                    + "images.txt records, you can ignore this warning, images dump was completed.)"
                )
                sys.exit()
            else:  # c_desc == c_images == len(images)
                complete = True
            if complete:
                # image dump is complete
                print("Image dump was completed in the previous session")
            else:
                # we resume from previous image, which may be corrupted (or missing
                # .desc)  by the previous session ctrl-c or abort
                Image.generate_image_dump(
                    config=config,
                    other=other,
                    images=images,
                    session=other["session"],
                )
