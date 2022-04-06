import TodoLabel
from PySide6.QtWidgets import QBoxLayout


class UploaderBoxLayout(QBoxLayout):
    def __init__(self, parent):

        self.parent = parent

        super.__init__(parent)

        self.todo_label = TodoLabel(self)
