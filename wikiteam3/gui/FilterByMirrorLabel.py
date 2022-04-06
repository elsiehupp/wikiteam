from PySide6.QtWidgets import QLabel


class FilterByMirrorLabel(QLabel):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent, text="Filter by mirror:")
        # self.grid(row=1, column=6)
