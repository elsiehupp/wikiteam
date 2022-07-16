from PySide6.QtWidgets import QComboBox


class FilterByDateComboBox(QComboBox):
    def __init__(self, parent):

        super(parent)

        self.string_variable = QStringVar(parent)
        self.string_variable.set("all")

        super.__init__(
            parent,
            self.string_variable,
            self.string_variable.get(),
            "2011",
            "2012",
        )
        # self.filter_by_date_combo_box.grid(row=1, column=5)
