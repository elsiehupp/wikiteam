from PySide6.QtWidgets import QLabel


class NotDownloadLabel(QLabel):
    def __init__(self, parent):

        super(parent)

        self.string_variable = QStringVar(parent)
        self.string_variable.set("Not downloaded: 0 (0.0 MB)")

        super.__init__(
            parent,
            textvariable=self.string_variable,
            background="white",
            width=27,
            # anchor=W,
        )
        # self.grid(row=0, column=4, columnspan=2)
