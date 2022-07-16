from PySide6.QtWidgets import QLabel


class FilterByDateLabel(QLabel):
    def __init__(self, parent):

        super(parent)

        super.__init__(
            parent,
            text="Filter by date:",
            width=15,
            # anchor=W
        )
        # self.grid(row=1, column=4)
