import webbrowser

import WikiTeamGui
from PySide6.QtWidgets import QMenu


class HelpMenu(QMenu):
    """help menu"""

    def __init__(self, parent):

        self.parent = parent

        parent.add_cascade(label="Help", menu=self)
        self.add_command(label="About", command=parent.callback)
        self.add_command(label="Help index", command=parent.callback)
        self.add_command(
            label="WikiTeam homepage",
            command=lambda: webbrowser.open_new_tab(WikiTeamGui.HOMEPAGE),
        )
