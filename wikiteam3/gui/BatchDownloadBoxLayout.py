import BatchDownloadWikiText
import BatchDownloadWikiUrlsLabel
from PySide6.QtWidgets import QBoxLayout


class BatchDownloadBoxLayout(QBoxLayout):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent, text="Batch download")
        # self.grid(row=1, column=0)

        self.batch_download_wiki_urls_label = BatchDownloadWikiUrlsLabel(self)
        self.batch_download_wiki_text = BatchDownloadWikiText(self)
