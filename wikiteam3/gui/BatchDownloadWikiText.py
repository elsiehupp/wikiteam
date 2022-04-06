from PySide6.QtWidgets import QText


class BatchDownloadWikiText(QText):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent, width=70, height=20)
        # self.grid(row=0, column=1)
