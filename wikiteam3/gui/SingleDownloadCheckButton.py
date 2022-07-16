import re
import threading

from PySide6.QtWidgets import QErrorMessage, QPushButton

from wikiteam3.dump_generator.api_info import ApiInfo
from wikiteam3.dump_generator.index_check import check_index


class SingleDownloadCheckButton(QPushButton):
    def __init__(self, parent):

        super(parent)

        super.__init__(
            parent,
            text="Check",
            command=lambda: threading.start_new_threading(self.check_url, ()),
            width=5,
        )
        # self.grid(row=0, column=3)

    def check_url(self):
        if re.search(
            r"(?im)^https?://[^/]+\.[^/]+/",
            self.single_download_box_layout.text_edit.get(),
        ):  # well-constructed URL?, one dot at least, aaaaa.com, but bb.aaaaa.com is allowed too
            if (
                self.parent.single_download_box_layout.combo_box.string_variable.get()
                == "api.php"
            ):
                self.parent.status_label.update_status_text(
                    "Please wait... Checking api.php..."
                )
                if ApiInfo(self.single_download_box_layout.text_edit.get()).check_api():
                    self.parent.single_download_box_layout.text_edit.config(
                        background="lightgreen"
                    )
                    self.parent.status_label.update_status_text(
                        "api.php is correct!", level="ok"
                    )
                else:
                    self.parent.single_download_box_layout.text_edit.config(
                        background="red"
                    )
                    self.parent.status_label.update_status_text(
                        "api.php is incorrect!", level="error"
                    )
            elif (
                self.parent.single_download_box_layout.combo_box.string_variable.get()
                == "index.php"
            ):
                self.parent.status_label.update_status_text(
                    "Please wait... Checking index.php..."
                )
                if check_index(self.single_download_box_layout.text_edit.get()):
                    self.parent.single_download_box_layout.text_edit.config(
                        background="lightgreen"
                    )
                    self.parent.status_label.update_status_text(
                        "index.php is OK!", level="ok"
                    )
                else:
                    self.parent.single_download_box_layout.text_edit.config(
                        background="red"
                    )
                    self.parent.status_label.update_status_text(
                        "index.php is incorrect!", level="error"
                    )
        else:
            QErrorMessage(
                "Error", "You have to write a correct api.php or index.php URL."
            )
