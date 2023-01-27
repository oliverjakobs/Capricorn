import tkinter as tk
from tkinter import ttk

class AboutDialog(tk.Toplevel):
    """Modal about dialog for idle"""
    def __init__(self, parent):
        """Create popup, do not return until tk widget destroyed."""
        super().__init__(parent)
        self.configure(borderwidth=5)
        # place dialog below parent if running htest
        self.geometry(f"+{parent.winfo_rootx()+30}+{parent.winfo_rooty()+30}")

        self.create_widgets()
        self.resizable(height=False, width=False)
        self.title('About')
        self.transient(parent)
        self.grab_set()
        
        self.button_ok.focus_set()
        self.bind('<Return>', self.ok)  # dismiss dialog
        self.bind('<Escape>', self.ok)  # dismiss dialog

        self.protocol("WM_DELETE_WINDOW", self.ok)

        self.deiconify()
        self.wait_window()

    def create_widgets(self):
        bg = "#bbbbbb"
        fg = "#000000"

        # content
        frame_content = tk.Frame(self, borderwidth=1, relief=tk.SOLID, bg=bg)

        header = tk.Label(frame_content, text="Capricorn", fg=fg, bg=bg, font=("Courier New", 24, 'bold'))
        header.grid(row=0, column=0, sticky=tk.W, padx=6, pady=10)

        byline_text = "Distraction free writing app." + (5 * '\n')
        byline = tk.Label(frame_content, text=byline_text, fg=fg, bg=bg)
        byline.grid(row=1, column=0, sticky=tk.W, padx=6, pady=5)
        github = tk.Label(frame_content, text="https://github.com/oliverjakobs/capricorn", fg=fg, bg=bg)
        github.grid(row=2, column=0, sticky=tk.W, padx=6, pady=6)

        separator = ttk.Separator(frame_content, orient=tk.HORIZONTAL)
        separator.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)

        # buttons
        frame_buttons = tk.Frame(frame_content, bg=bg)

        self.btn_readme = tk.Button(frame_buttons, text="README", width=8, highlightbackground=bg)
        self.btn_readme.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_copyright = tk.Button(frame_buttons, text="Copyright", width=8, highlightbackground=bg)
        self.btn_copyright.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_credits = tk.Button(frame_buttons, text="Credits", width=8, highlightbackground=bg)
        self.btn_credits.pack(side=tk.LEFT, padx=10, pady=10)

        frame_buttons.grid(row=4, column=0, sticky=tk.NSEW)

        # footer
        frame_footer = tk.Frame(self)

        self.button_ok = tk.Button(frame_footer, text="Close", padx=6, command=self.ok)
        self.button_ok.pack(padx=5, pady=5)

        frame_content.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        frame_footer.pack(side=tk.BOTTOM, fill=tk.X)


    def ok(self, event=None):
        "Dismiss help_about dialog."
        self.grab_release()
        self.destroy()