from PySide6.QtWidgets import QComboBox


class DownloaderComboBox(QComboBox):
    def __init__(self, parent):

        self.parent = parent

        self.string_variable = QStringVar(parent)
        self.string_variable.set("all")

        super.__init__(
            parent,
            self.string_variable,
            self.string_variable.get(),
            "Gentoo Wiki",
            "OpenSuSE",
            "Referata",
            "ShoutWiki",
            "Unknown",
            "Wikanda",
            "WikiFur",
            "Wikimedia",
            "WikiTravel",
            "Wikkii",
        )
        # self.grid(row=1, column=1)
