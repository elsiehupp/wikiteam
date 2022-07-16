from PySide6.QtWidgets import QComboBox


class FilterByMirrorComboBox(QComboBox):
    def __init__(self, parent):

        super(parent)

        self.string_variable = QStringVar(parent)
        self.string_variable.set("all")

        super.__init__(
            parent,
            self.string_variable,
            self.string_variable.get(),
            "Google Code",
            "Internet Archive",
            "ScottDB",
        )
        # self.grid(row=1, column=7)
