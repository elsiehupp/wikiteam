from PySide6.QtWidgets import QPlainTextEdit


class SingleDownloadTextEdit(QPlainTextEdit):
    def __init__(self, parent):

        super(parent)

        self.width = 40

        # self.grid(row=0, column=1)
        # self.bind("<Return>", (lambda event: self.check_url()))
