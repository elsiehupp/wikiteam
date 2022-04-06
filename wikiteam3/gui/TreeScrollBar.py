from PySide6.QtWidgets import QScrollBar


class TreeScrollBar(QScrollBar):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent)
        # self.grid(row=2, column=9, sticky=W + E + N + S)
