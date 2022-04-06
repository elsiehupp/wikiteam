from PySide6.QtWidgets import QLabel


class WikiUrlLabel(QLabel):
    def __init__(self, parent, text):

        self.parent = parent

        # single download labelframe
        super.__init__(parent, text)
        # self.grid(row=0, column=0)
