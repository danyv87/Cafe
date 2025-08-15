import tkinter as tk
from typing import Callable, Iterable, List, Any


class HistoryReportFrame(tk.Frame):
    """Common frame to display history records with a Listbox and Scrollbar."""

    def __init__(
        self,
        master,
        title: str,
        records: Iterable[Any],
        row_formatter: Callable[[Any], List[str]],
        width: int = 90,
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        tk.Label(self, text=title, font=("Helvetica", 16, "bold")).pack(pady=10)

        frame_list = tk.Frame(self)
        frame_list.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_list, orient=tk.VERTICAL)
        listbox = tk.Listbox(frame_list, width=width, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if not records:
            listbox.insert(tk.END, "No hay registros.")
        else:
            for record in records:
                for line in row_formatter(record):
                    listbox.insert(tk.END, line)

        # Expose listbox for further manipulation if needed
        self.listbox = listbox
