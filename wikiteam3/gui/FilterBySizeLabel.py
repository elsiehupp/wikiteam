from PySide6.QtWidgets import QLabel


class FilterBySizeLabel(QLabel):
    def __init__(self, parent):

        super(parent)

        super.__init__(
            parent,
            text="Filter by size:",
            width=15
            # anchor=W)
        )
        # self.grid(row=1, column=2)
