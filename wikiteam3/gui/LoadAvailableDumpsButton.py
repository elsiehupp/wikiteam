import os
import re
import threading

import requests
import WikiTeamGui
from PySide6.QtWidgets import QPushButton


class LoadAvailableDumpsButton(QPushButton):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(
            parent,
            text="Load available dumps",
            command=lambda: threading.start_new_threading(
                self.load_available_dumps, ()
            ),
            width=15,
        )
        # self.grid(row=3, column=0)

    def load_available_dumps(self):
        if self.parent.block:
            self.parent.blocked()
            return
        else:
            self.parent.block = True
        if self.dumps:
            self.parent.delete_available_dumps()
        iaregexp = r'/download/[^/]+/(?P<filename>[^>]+\.7z)">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a>'
        self.urls = [
            [
                "Google Code",
                "https://code.google.com/p/wikiteam/downloads/list?num=5000&start=0",
                r'(?im)detail\?name=(?P<filename>[^&]+\.7z)&amp;can=2&amp;q=" style="white-space:nowrap">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a></td>',
            ],
            [
                "Internet Archive",
                "http://www.archive.org/details/referata.com-20111204",
                iaregexp,
            ],
            [
                "Internet Archive",
                "http://www.archive.org/details/WikiTeamMirror",
                iaregexp,
            ],
            [
                "ScottDB",
                "http://mirrors.sdboyd56.com/WikiTeam/",
                r'<a href="(?P<filename>[^>]+\.7z)">(?P<size>[\d\.]+ (?:KB|MB|GB|TB))</a>',
            ],
            [
                "Wikimedia",
                "http://dumps.wikimedia.org/backup-index.html",
                r'(?P<size>)<a href="(?P<filename>[^>]+)">[^>]+</a>: <span class=\'done\'>Dump complete</span></li>',
            ],
        ]
        wikifarms_r = re.compile(r"(%s)" % ("|".join(WikiTeamGui.wikifarms.keys())))
        # count = 0
        for mirror, url, regexp in self.urls:
            print("Loading data from", mirror, url)
            self.parent.status_label.update_status_text(
                update_status_text=f"Please wait... Loading data from {mirror} {url}"
            )
            file = requests.Session().get(url)
            match = re.compile(regexp).finditer(file.read())
            for i in match:
                filename = i.group("filename")
                if mirror == "Wikimedia":
                    filename = "%s-pages-meta-history.xml.7z" % (
                        re.sub("/", "-", filename)
                    )
                wikifarm = "Unknown"
                if re.search(wikifarms_r, filename):
                    wikifarm = re.findall(wikifarms_r, filename)[0]
                wikifarm = WikiTeamGui.wikifarms[wikifarm]
                size = i.group("size")
                if not size:
                    size = "Unknown"
                date = "Unknown"
                if re.search(r"\-(\d{8})[\.-]", filename):
                    date = re.findall(r"\-(\d{4})(\d{2})(\d{2})[\.-]", filename)[0]
                    date = f"{date[0]}-{date[1]}-{date[2]}"
                elif re.search(r"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename):
                    date = re.findall(r"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename)[0]
                downloadurl = ""
                if mirror == "Google Code":
                    downloadurl = "https://wikiteam.googlecode.com/files/" + filename
                elif mirror == "Internet Archive":
                    downloadurl = (
                        re.sub(r"/details/", r"/download/", url) + "/" + filename
                    )
                elif mirror == "ScottDB":
                    downloadurl = url + "/" + filename
                elif mirror == "Wikimedia":
                    downloadurl = (
                        "http://dumps.wikimedia.org/"
                        + filename.split("-")[0]
                        + "/"
                        + re.sub("-", "", date)
                        + "/"
                        + filename
                    )
                downloaded = self.is_dump_downloaded(filename)
                self.dumps.append(
                    [filename, wikifarm, size, date, mirror, downloadurl, downloaded]
                )
        self.parent.dumps.sort()
        self.parent.show_available_dumps()
        self.parent.filter_available_dumps()
        self.parent.status_label.update_status_text(
            update_status_text="Loaded %d available dumps!" % (len(self.dumps)),
            level="ok",
        )
        self.parent.block = False

    def is_dump_downloaded(self, filename):
        # improve, size check or md5sum?
        if filename:
            filepath = (
                self.parent.downloadpath
                and self.parent.downloadpath + "/" + filename
                or filename
            )
            if os.path.exists(filepath):
                return True

        """estsize = os.path.getsize(filepath)
                count = 0
                while int(estsize) >= 1024:
                    estsize = estsize/1024.0
                    count += 1
                estsize = '%.1f %s' % (estsize, ['', 'KB', 'MB', 'GB', 'TB'][count])"""

        return False
