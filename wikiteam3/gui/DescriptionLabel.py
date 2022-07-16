from PySide6.QtWidgets import QLabel


class DescriptionLabel(QLabel):
    def __init__(self, parent):

        super(parent)

        super.__init__("", parent)  # font=("Arial", 10))
        # description
        # self.description_label.grid(row=0, column=0, columnspan=1)
        # self.footer_label = QLabel(self.master, text="%s (version %s). This program is free software (GPL v3 or higher)" % (NAME, VERSION), anchor=W, justify=LEFT, font=("Arial", 10))
        # self.footer_label.grid(row=2, column=0, columnspan=1)
