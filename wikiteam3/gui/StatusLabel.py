import random

import MenuBar
from PySide6.QtWidgets import QLabel


class StatusLabel(QLabel):
    def __init__(self, parent):

        super(parent)

        # statusbar
        super.__init__(parent)
        self.setText(
            "Welcome to WikiTeam tools. What wiki do you want to preserve today?"
        )
        #     bd=1,
        #     background="grey",
        #     justify=LEFT,
        #     relief=SUNKEN,
        # )
        # self.status_label.grid(row=4, column=0, columnspan=10, sticky=W + E)

        self.menu_bar = MenuBar(self)

    def sum_sizes(self, sizes):
        total = 0
        for size in sizes:
            if size.endswith("KB"):
                total += float(size.split(" ")[0])
            elif size.endswith("MB"):
                total += float(size.split(" ")[0]) * 1024
            elif size.endswith("GB"):
                total += float(size.split(" ")[0]) * 1024 * 1024
            elif size.endswith("TB"):
                total += float(size.split(" ")[0]) * 1024 * 1024 * 1024
            elif not size or size.lower() == "unknown":
                pass
            else:
                total += size
        return total / 1024  # MB

    def tree_sort_column(self, column, reverse=False):
        list = [(self.tree.set(i, column), i) for i in self.tree.get_children("")]
        list.sort(reverse=reverse)
        for index, (val, i) in enumerate(list):
            self.tree.move(i, "", index)
        self.tree.heading(
            column,
            command=lambda: self.tree_sort_column(column=column, reverse=not reverse),
        )

    def download_progress(self, block_count, block_size, total_size):
        try:
            total_mb = total_size / 1024 / 1024.0
            downloaded = block_count * (block_size / 1024 / 1024.0)
            percent = downloaded / (total_mb / 100.0)
            if not random.randint(0, 10):
                update_status_text = (
                    "{:.1f} MB of {:.1f} MB downloaded ({:.1f}%)".format(
                        downloaded,
                        total_mb,
                        percent <= 100 and percent or 100,
                    )
                )
                self.parent.status_label.update_status_text(
                    update_status_text, level="ok"
                )
            # sys.stdout.write("%.1f MB of %.1f MB downloaded (%.2f%%)" %(downloaded, total_mb, percent))
            # sys.stdout.flush()
        except Exception:
            pass

    def show_available_dumps(self):
        count = 0
        for filename, wikifarm, size, date, mirror, url, downloaded in self.dumps:
            self.tree.insert(
                "",
                "end",
                str(count),
                text=filename,
                values=(
                    filename,
                    wikifarm,
                    size,
                    date,
                    mirror,
                    downloaded and "Downloaded" or "Not downloaded",
                ),
                tags=(downloaded and "downloaded" or "nodownloaded",),
            )
            count += 1

    def update_status_text(self, new_status_text="", level=""):
        levels = {"ok": "lightgreen", "warning": "yellow", "error": "red"}
        if level.lower() in levels:
            print(f"{level.upper()}: {new_status_text}")
            self.config(
                text=f"{level.upper()}: {new_status_text}",
                background=levels[level.lower()],
            )
        else:
            print(new_status_text)
            self.config(text=new_status_text, background="grey")
