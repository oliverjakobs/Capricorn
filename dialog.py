import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from lib.extendedTk import DigitEntry, ColorEntry
from lib.autocomplete import AutocompleteCombobox

#============================================================================
# about
#============================================================================
class AboutDialog(tk.Toplevel):
    def __init__(self, parent, title=None):
        """Create popup, do not return until tk widget destroyed."""
        super().__init__(parent)

        self.title(title or 'About')
        x = parent.winfo_rootx() + 30
        y = parent.winfo_rooty() + 30
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(parent)

        self.button_ok.focus_set()
        self.bind('<Return>', self.ok)  # dismiss dialog
        self.bind('<Escape>', self.ok)  # dismiss dialog

        self.protocol("WM_DELETE_WINDOW", self.ok)

        self.grab_set()
        self.wm_deiconify()
        self.wait_window()

    def create_widgets(self):
        bg = "#bbbbbb"
        fg = "#000000"

        self.configure(borderwidth=5)

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


#============================================================================
# preferences
#============================================================================
class PrefDialog(tk.Toplevel):
    def __init__(self, parent, config, apply, title=None):
        """Create dialog, do not return until tk widget destroyed."""
        super().__init__(parent)

        self.apply_cb = apply

        self.title(title or 'Preferences')
        x = parent.winfo_rootx() + 20
        y = parent.winfo_rooty() + 30
        self.geometry(f'+{x}+{y}')

        self.create_widgets(config)
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.grab_set()
        self.wm_deiconify()
        self.wait_window()

    def create_widgets(self, config):
        frame_content = ttk.Frame(self)

        self.frames = [
            WorkspaceFrame(frame_content, "Workspace", config['workspace']),
            ColorFrame(frame_content, "Colors", config['colors'])
        ]

        for frame in self.frames:
            frame.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)

        frame_content.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        # buttons
        frame_btns = ttk.Frame(self, style='Buttonframe.TFrame')
        frame_btns.configure(borderwidth=8)

        buttons = {
            'Ok':     self.ok,
            'Apply':  self.apply,
            'Cancel': self.cancel
        }

        buttons_args = {
            'takefocus': tk.FALSE,
            'width': 8
        }

        for text, cmd in buttons.items():
            btn = ttk.Button(frame_btns, text=text, command=cmd, **buttons_args)
            btn.pack(side=tk.LEFT, padx=5)

        frame_btns.pack(side=tk.BOTTOM, expand=tk.TRUE, fill=tk.X)

    def ok(self):
        """Apply config changes, then dismiss dialog. """
        self.apply()
        self.cancel()

    def apply(self):
        """Apply config changes and leave dialog open. """

        config = {}
        for frame in self.frames:
            config |= frame.get_config()

        self.apply_cb(config)

    def cancel(self):
        """Dismiss config dialog. """
        self.grab_release()
        self.destroy()


class ColorFrame(ttk.LabelFrame):
    def __init__(self, master, text, config):
        super().__init__(master, text=text)

        self.colors = {}
        for name, color in config.items():
            self.colors[name] = tk.StringVar(self, color.replace('#', ''))

        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)

        row = 0
        for color, var in self.colors.items():
            label_color = ttk.Label(self, text=color)
            entry_color = ColorEntry(self, width=6, textvariable=var)

            label_color.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry_color.grid(row=row, column=1, sticky=tk.E, padx=10, pady=5)

            row += 1

    def get_config(self):
        return { 'colors': {k: f"#{v.get()}" for k,v in self.colors.items()} }


class WorkspaceFrame(ttk.LabelFrame):
    def __init__(self, master, text, config):
        super().__init__(master, text=text)

        self.text_width = tk.IntVar(self, config['text_width'])

        self.font_family = tk.StringVar(self, 'Courier New')
        self.font_size = tk.IntVar(self, 10)

        self.create_widgets()

    def create_widgets(self):
        # text width
        frame_width = ttk.Frame(self)
        frame_width.columnconfigure(0, weight=1)

        label_width = ttk.Label(frame_width, text="Text Width")
        label_width.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        entry_width = DigitEntry(frame_width, justify=tk.RIGHT, width=6, textvariable=self.text_width)
        entry_width.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        frame_width.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.X)

        # font
        frame_font = ttk.Frame(self)
        frame_font.columnconfigure(0, weight=1)

        label_font = ttk.Label(frame_font, text="Font")
        label_font.columnconfigure(0, weight=1)
        label_font.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        entry_family = AutocompleteCombobox(frame_font, width=16, textvariable=self.font_family)
        entry_family.set_completion_list(sorted(set(tkfont.families(self))))
        entry_family.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)

        entry_size = DigitEntry(frame_font, justify=tk.RIGHT, width=6, textvariable=self.font_size)
        entry_size.grid(row=0, column=2, sticky=tk.E, padx=10, pady=5)

        frame_font.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.X)

    def get_config(self):
        config = {
            'font': f'"{self.font_family.get()}" {self.font_size.get()}',
            'text_width': self.text_width.get()
        }

        return { 'workspace': config }