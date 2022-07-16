from BatchDownloadBoxLayout import BatchDownloadBoxLayout
from PySide6.QtWidgets import QBoxLayout
from SingleDownloadBoxLayout import SingleDownloadBoxLayout


class DumpGeneratorBoxLayout(QBoxLayout):
    def __init__(self, parent):

        super(parent)

        self.single_download_box_layout = SingleDownloadBoxLayout(self)
        self.insertItem(self.single_download_box_layout)

        self.batch_download_box_layout = BatchDownloadBoxLayout(self)
        self.insertItem(self.batch_download_box_layout)
