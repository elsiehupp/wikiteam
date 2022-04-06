from PySide6.QtWidgets import QLabel


class FilterByWikiFarmLabel(QLabel):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(
            parent,
            text="Filter by wikifarm:",
            width=15,  # anchor=W
        )
        # self.grid(row=1, column=0)
