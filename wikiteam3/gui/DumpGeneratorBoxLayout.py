from BatchDownloadBoxLayout import BatchDownloadBoxLayout
from PySide6.QtWidgets import QBoxLayout
from SingleDownloadBoxLayout import SingleDownloadBoxLayout


class DumpGeneratorBoxLayout(QBoxLayout):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent)

        self.single_download_box_layout = SingleDownloadBoxLayout(self)
        self.batch_download_box_layout = BatchDownloadBoxLayout(self)
