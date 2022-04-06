#!/usr/bin/env python3

# Copyright (C) 2011-2012 WikiTeam
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

import os
import platform
import time

import DescriptionLabel
import ExitPrompt
import StatusLabel
import TabWidget

# from PySide6 import QtCore, QtGui
# https://doc.qt.io/qtforpython/PySide6/QtWidgets/index.html
from PySide6.QtWidgets import QApplication, QErrorMessage


class WikiTeamGui(QApplication):

    """
    TODO:

    * basic: GUI to download just a wiki

    * advanced: batch downloads, upload to Internet Archive or anywhere
    """

    wikifarms: dict = {
        "gentoo_wikicom": "Gentoo Wiki",
        "opensuseorg": "OpenSuSE",
        "referatacom": "Referata",
        "shoutwikicom": "ShoutWiki",
        "Unknown": "Unknown",
        "wikanda": "Wikanda",
        "wikifur": "WikiFur",
        "wikimedia": "Wikimedia",
        "wikitravelorg": "WikiTravel",
        "wikkii": "Wikkii",
    }

    NAME: str = "WikiTeam tools"
    VERSION: str = "0.1"
    HOMEPAGE: str = "https://code.google.com/p/wikiteam/"
    IS_LINUX: bool = platform.system().lower() == "linux"
    PATH: str = os.path.dirname(__file__)
    if PATH:
        os.chdir(PATH)

    def __init__(self, master):
        self.master = master
        self.dumps = []
        self.downloadpath = "downloads"
        self.block = False

        width = 1050
        height = 560
        # calculate position x, y
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.title("%s (version %s)" % WikiTeamGui.NAME, WikiTeamGui.VERSION)
        self.protocol("WM_DELETE_WINDOW", ExitPrompt)
        # logo
        # imagelogo = PhotoImage(file = 'logo.gif')
        # labellogo = QLabel(root, image=imagelogo)
        # labellogo.grid(row=0, column=0, rowspan=3, sticky=W)

        # interface elements
        # progressbar
        # self.value = 0
        # self.progressbar = QProgressbar(self.master, orient=HORIZONTAL, value=self.value, mode='determinate')
        # self.progressbar.grid(row=0, column=0, columnspan=1, sticky=W+E)
        # self.run()

        self.description_label = DescriptionLabel(self)
        self.tab_widget = TabWidget(self)
        self.status_label = StatusLabel(self.master)

    def blocked(self):
        QErrorMessage("Error", "There is a task in progress. Please, wait.")

    def run(self):
        for i in range(10):
            time.sleep(0.1)
            self.value += 10

        """
        #get parameters selected
        params = ['--api=http://www.archiveteam.org/api.php', '--xml']

        #launch dump
        main(params)

        #check dump
        """


if __name__ == "__main__":
    root = WikiTeamGui
    app = WikiTeamGui(root)
    root.mainloop()
