from PySide6.QtWidgets import QPushButton


class ClearAvailableDumpsButton(QPushButton):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(
            parent, text="Clear list", command=self.delete_available_dumps, width=10
        )
        # self.grid(row=3, column=8, columnspan=2)

    def delete_available_dumps(self):
        # really delete dump list and clear tree
        self.clear_available_dumps()
        self.dumps = []  # reset list
