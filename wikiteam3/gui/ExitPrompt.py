from PySide6.QtWidgets import QMessageBox


class ExitPrompt(QMessageBox):
    def __init__(self, parent):

        self.parent = parent

        super.__init__()
        # if QMessageBox.askokcancel("Quit", "Do you really wish to exit?"):
        self.setText("Quit")
        self.setInformativeText("Do you really wish to exit?")
        self.setStandardButtons(QMessageBox.Yes, QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        user_response = self.exec()
        if user_response == QMessageBox.Yes:
            parent.root.destroy()
        return
