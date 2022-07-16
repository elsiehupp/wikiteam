from PySide6.QtWidgets import QComboBox


class SingleDownloadComboBox(QComboBox):
    def __init__(self, parent):

        super(parent)

        self.string_variable = QStringVar(parent)
        self.string_variable.set("api.php")

        self.addItem(self.string_variable)
        self.addItem(self.string_variable.get())
        self.addItem("index.php")
        # self.grid(row=0, column=2)
