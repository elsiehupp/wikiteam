from PySide6.QtWidgets import QLabel


class BatchDownloadWikiUrlsLabel(QLabel):
    def __init__(self, parent):

        self.parent = parent

        # batch download labelframe
        super.__init__(parent, text="Wiki URLs:")
        # self.grid(row=0, column=0)
