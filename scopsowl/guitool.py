# ------------------
# Import Library
# ------------------
import tkinter as tk
import logging


# ------------------
# Errors and logs
# ------------------
logger = logging.getLogger('scops_owl.guitool')

# ------------------
# Class
# ------------------
class TextBox(tk.Text):
    def __init__(self, master, label, width, textwrap):
        # make the text box with x and y scrollbar
        self.frame = tk.Frame(master)
        self.block = dict()
        super().__init__(
            self.frame,
            borderwidth=3,
            width=width,
            relief=tk.SUNKEN,
            wrap=textwrap
        )
        self.block['label'] = tk.Label(self.frame, text=label)
        self.block['scroll_x'] = tk.Scrollbar(
            self.frame,
            command=self.xview,
            orient=tk.HORIZONTAL
        )
        self.configure(xscrollcommand=self.block['scroll_x'].set)
        self.block['scroll_y'] = tk.Scrollbar(
            self.frame,
            command=self.yview,
            orient=tk.VERTICAL
        )
        self.configure(yscrollcommand=self.block['scroll_y'].set)

    def grid(self, row, column, ** vars):
        self.frame.grid(row=row, column=column, **vars)
        self.block['label'].grid(row=0, column=0)
        super().grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.block['scroll_x'].grid(row=2, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.block['scroll_y'].grid(row=1, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

# ------------------


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.configure(state=tk.DISABLED)
        self.widget.tag_config("INFO", foreground="black")
        self.widget.tag_config("DEBUG", foreground="grey")
        self.widget.tag_config("WARNING", foreground="orange")
        self.widget.tag_config("ERROR", foreground="red")
        self.widget.tag_config("CRITICAL", foreground="red", underline=1)

    def emit(self, record):
        self.widget.configure(state=tk.NORMAL)
        # Append message (record) to the widget
        self.widget.insert(tk.END, self.format(record) + '\n', record.levelname)
        self.widget.see(tk.END)  # Scroll to the bottom
        self.widget.configure(state=tk.DISABLED)
        self.widget.update()  # Refresh the widget

# ------------------
# EOF
# ------------------
