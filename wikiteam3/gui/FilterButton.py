from PySide6.QtWidgets import QPushButton


class FilterButton(QPushButton):
    def __init__(self, parent):

        super(parent)

        super.__init__(
            parent, text="Filter!", command=self.filter_available_dumps, width=7
        )
        # self.grid(row=1, column=8)

    def filter_available_dumps(self):
        self.parent.clear_available_dumps()
        self.parent.show_available_dumps()
        sizes = []
        downloadedsizes = []
        nodownloadedsizes = []
        for i in range(len(self.dumps)):
            if (
                self.parent.downloader_combo_box.string_variable.get() == "all"
                and self.parent.size_combo_box.string_variable.get() == "all"
                and self.parent.filter_by_date_combo_box.string_variable.get() == "all"
                and self.parent.filter_by_mirror_menu.string_variable.get() == "all"
            ):
                sizes.append(self.parent.dumps[i][2])
                if self.dumps[i][6]:
                    downloadedsizes.append(self.parent.dumps[i][2])
                else:
                    nodownloadedsizes.append(self.parent.dumps[i][2])
            elif (
                (
                    self.parent.downloader_combo_box.string_variable.get() != "all"
                    and not self.parent.downloader_combo_box.string_variable.get()
                    == self.parent.dumps[i][1]
                )
                or (
                    self.parent.size_combo_box.string_variable.get() != "all"
                    and not self.parent.string_variable.get() in self.parent.dumps[i][2]
                )
                or (
                    self.parent.filter_by_date_combo_box.string_variable.get() != "all"
                    and not self.parent.filter_by_date_combo_box.string_variable.get()
                    in self.parent.dumps[i][3]
                )
                or (
                    self.parent.filter_by_mirror_menu.string_variable.get() != "all"
                    and not self.parent.filter_by_mirror_menu.string_variable.get()
                    in self.parent.dumps[i][4]
                )
            ):
                self.parent.tree.detach(str(i))  # hide this item
                sizes.append(self.parent.dumps[i][2])
                if self.parent.dumps[i][6]:
                    downloadedsizes.append(self.parent.dumps[i][2])
                else:
                    nodownloadedsizes.append(self.parent.dumps[i][2])
        self.parent.available_dumps_label.string_variable.set(
            "Available dumps: %d (%.1f MB)" % (len(sizes), self.sum_sizes(sizes))
        )
        self.parent.downloaded_label.string_variable.set(
            "Downloaded: %d (%.1f MB)"
            % (len(downloadedsizes), self.sum_sizes(downloadedsizes))
        )
        self.parent.not_downloaded_label.string_variable.set(
            "Not downloaded: %d (%.1f MB)"
            % (len(nodownloadedsizes), self.sum_sizes(nodownloadedsizes))
        )
