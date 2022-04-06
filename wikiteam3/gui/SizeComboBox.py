from PySide6.QtWidgets import QComboBox


class SizeComboBox(QComboBox):
    def __init__(self, parent):

        self.parent = parent

        self.string_variable = QStringVar(parent)
        self.string_variable.set("all")

        super.__init__(
            parent,
            self.string_variable,
            self.string_variable.get(),
            "KB",
            "MB",
            "GB",
            "TB",
        )
        # self.grid(row=1, column=3)
