from PySide6.QtWidgets import QLabel


class AvailableDumpsLabel(QLabel):
    def __init__(self, parent):

        super(parent)
        self.text = "Available dumps: 0 (0.0 MB)"

        # downloader tab (2)
        # super.__init__(
        #     parent,
        #     textvariable=self.string_variable,
        #     width=27,
        #     # anchor=W
        # )
        # self.grid(row=0, column=0, columnspan=2)
