import TodoLabel
from PySide6.QtWidgets import QBoxLayout


class UploaderBoxLayout(QBoxLayout):
    def __init__(self, parent):

        super(parent)

        self.todo_label = TodoLabel(self)
        self.insertItem(self.todo_label)
