import HelpMenu
from PySide6.QtWidgets import QMenu, QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent):

        super(parent)

        # begin menu
        super.__init__(self, parent)
        self.parent.master.config(menu=self)
        self.file_menu = HelpMenu(self)
        self.help_menu = QMenu(self)
        # end menu

    def callback(self):
        self.parent.status_label.update_status_text(
            "Feature not implemented for the moment. Contributions are welcome.",
            level="warning",
        )
