from PySide6.QtWidgets import QBoxLayout
from SingleDownloadCheckButton import SingleDownloadCheckButton
from SingleDownloadComboBox import SingleDownloadComboBox
from SingleDownloadTextEdit import SingleDownloadTextEdit


class SingleDownloadBoxLayout(QBoxLayout):
    def __init__(self, parent):

        self.parent = parent

        # dump generator tab (1)
        super.__init__(parent, text="Single download")
        # self.grid(row=0, column=0)

        self.text_edit = SingleDownloadTextEdit(self)  # width=40)
        self.combo_box = SingleDownloadComboBox(self)
        self.check_button = SingleDownloadCheckButton(self)
