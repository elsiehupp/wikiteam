from PySide6.QtWidgets import QBoxLayout
from SingleDownloadCheckButton import SingleDownloadCheckButton
from SingleDownloadComboBox import SingleDownloadComboBox
from SingleDownloadTextEdit import SingleDownloadTextEdit


class SingleDownloadBoxLayout(QBoxLayout):
    def __init__(self, parent):

        super(parent)

        # dump generator tab (1)
        self.text = "Single download"
        # self.grid(row=0, column=0)

        self.text_edit = SingleDownloadTextEdit(self)
        self.insertItem(self.text_edit)

        self.combo_box = SingleDownloadComboBox(self)
        self.insertItem(self.combo_box)

        self.check_button = SingleDownloadCheckButton(self)
        self.insertItem(self.check_button)
