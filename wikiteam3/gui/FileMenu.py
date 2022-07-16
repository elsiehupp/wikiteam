import ExitPrompt
from PySide6.QtWidgets import QMenu


class FileMenu(QMenu):
    """file menu"""

    def __init__(self, parent):

        super(parent)

        parent.add_cascade(label="File", menu=self)
        self.add_command(label="Preferences", command=parent.callback)
        self.add_separator()
        self.add_command(label="Exit", command=ExitPrompt)
