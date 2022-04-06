from PySide6.QtWidgets import QTreeView


class DumpListTreeView(QTreeView):
    def __init__(self, parent):

        self.parent = parent

        columns = ("dump", "wikifarm", "size", "date", "mirror", "status")

        super.__init__(
            parent,
            height=20,
            columns=columns,
            show="headings",
            yscrollcommand=self.parent.tree_scroll_bar.set,
        )

        self.parent.tree_scroll_bar.config(command=self.yview)
        self.column("dump", width=495, minwidth=200, anchor="center")
        self.heading("dump", text="Dump")
        self.column("wikifarm", width=100, minwidth=100, anchor="center")
        self.heading("wikifarm", text="Wikifarm")
        self.column("size", width=100, minwidth=100, anchor="center")
        self.heading("size", text="Size")
        self.column("date", width=100, minwidth=100, anchor="center")
        self.heading("date", text="Date")
        self.column("mirror", width=120, minwidth=120, anchor="center")
        self.heading("mirror", text="Mirror")
        self.column("status", width=120, minwidth=120, anchor="center")
        self.heading("status", text="Status")
        self.grid(row=2, column=0, columnspan=9)  # sticky=W + E + N + S)
        [
            self.heading(
                column,
                text=column,
                command=lambda: self.tree_sort_column(column=column, reverse=False),
            )
            for column in columns
        ]
        # self.bind("<Double-1>", (lambda: threading.start_new_threading(self.download_dump, ())))
        self.tag_configure("downloaded", background="lightgreen")
        self.tag_configure("nodownloaded", background="white")

    def clear_available_dumps(self):
        # clear tree
        for i in range(len(self.dumps)):
            self.delete(str(i))
