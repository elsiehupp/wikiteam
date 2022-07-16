import os
import threading
import urllib

from PySide6.QtWidgets import QErrorMessage, QPushButton


class DownloadSelectionButton(QPushButton):
    def __init__(self, parent):

        super(parent)

        super.__init__(
            parent,
            text="Download selection",
            command=lambda: threading.start_new_threading(self.download_dump, ()),
            width=15,
        )
        # self.grid(row=3, column=4)

    def download_dump(self, event=None):
        if self.parent.block:
            self.parent.blocked()
            return
        else:
            self.parent.block = True
        items = self.parent.tree.selection()
        if items:
            if not os.path.exists(self.parent.downloadpath):
                os.makedirs(self.parent.downloadpath)
            count = 0
            count_2 = 0
            for item in items:
                filepath = (
                    self.parent.downloadpath
                    and self.parent.downloadpath + "/" + self.dumps[int(item)][0]
                    or self.parent.dumps[int(item)][0]
                )
                if os.path.exists(filepath):
                    self.parent.status_label.update_status_text(
                        "That dump was downloaded before", level="ok"
                    )
                    count_2 += 1
                else:
                    self.parent.status_label.update_status_text(
                        "[%d of %d] Downloading %s from %s"
                        % (
                            count + 1,
                            len(items),
                            self.parent.tree.item(item, "text"),
                            self.parent.dumps[int(item)][5],
                        )
                    )
                    urllib.urlretrieve(
                        self.parent.dumps[int(item)][5],
                        filepath,
                        reporthook=self.parent.download_progress,
                    )
                    update_status_text = (
                        "{} size is {} bytes large. Download successful!".format(
                            self.parent.dumps[int(item)][0],
                            os.path.getsize(filepath),
                        )
                    )
                    self.parent.status_label.update_status_text(
                        update_status_text=update_status_text, level="ok"
                    )
                    count += 1
                self.parent.dumps[int(item)] = self.dumps[int(item)][:6] + ["True"]
            if count + count_2 == len(items):
                self.parent.status_label.update_status_text(
                    "Downloaded %d of %d%s."
                    % (
                        count,
                        len(items),
                        count_2
                        and " (and %d were previously downloaded)" % (count_2)
                        or "",
                    ),
                    level="ok",
                )
            else:
                self.parent.status_label.update_status_text(
                    "Problems in %d dumps. Downloaded %d of %d (and %d were previously downloaded)."
                    % (len(items) - (count + count_2), count, len(items), count_2),
                    level="error",
                )
        else:
            QErrorMessage("Error", "You have to select some dumps to download.")
        self.parent.clear_available_dumps()
        self.parent.show_available_dumps()
        self.parent.filter_available_dumps()
        self.parent.block = False
