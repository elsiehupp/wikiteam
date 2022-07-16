from PySide6.QtWidgets import QPushButton


class ClearAvailableDumpsButton(QPushButton):
    def __init__(self, parent):

        super(parent)

        self.text = "Clear list"
        self.width = 10
        self.setCheckable(True)
        self.clicked.connect(self.self.delete_available_dumps)

        # self.grid(row=3, column=8, columnspan=2)

    def delete_available_dumps(self):
        # really delete dump list and clear tree
        self.clear_available_dumps()
        self.dumps = []  # reset list
