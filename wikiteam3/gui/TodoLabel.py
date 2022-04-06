from PySide6.QtWidgets import QLabel


class TodoLabel(QLabel):
    def __init__(self, parent):

        self.parent = parent

        # uploader tab (3)
        super.__init__(parent, text="todo...")
        # self.grid(row=0, column=0)
