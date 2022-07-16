from DownloaderBoxLayout import DownloaderBoxLayout
from DumpGeneratorBoxLayout import DumpGeneratorBoxLayout
from PySide6.QtWidgets import QTabWidget
from UploaderBoxLayout import UploaderBoxLayout


class TabWidget(QTabWidget):
    def __init__(self, parent):

        super(parent)

        # begin tabs
        # self.tab_widget.grid(row=1, column=0, columnspan=1, sticky=W + E + N + S)

        self.dump_generator_box_layout = DumpGeneratorBoxLayout(self)
        self.addTab(self.dump_generator_box_layout, label="Dump generator")
        self.downloader_box_layout = DownloaderBoxLayout(self)
        self.uploader_box_layout = UploaderBoxLayout(self)
        self.addTab(self.downloader_box_layout, label="Downloader")
        self.addTab(self.uploader_box_layout, label="Uploader")
