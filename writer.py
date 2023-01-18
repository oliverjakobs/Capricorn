import os, sys, re
from configparser import ConfigParser
from glob import glob

# import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# import own stuff
from extendedTk import *

BUILTIN_THEME = """
# Theme dark
namespace eval ttk::theme::dark {
    # Style colors
    array set colors {
        -fg_main    "#e1e4e8"
        -bg_main    "#454545"
        -bg_status  "#2f2f2f"
        -fg_text    "#000000"
        -bg_text    "#f1f1f1"
        -fg_title   "#b392f0"
        -scrollbar  "#6f6f6f"
    }

    set base_font {"Courier New" 10}
    set title_font {"Courier New" 24 bold}

    # Create style
    ttk::style theme create dark -parent default -settings {
        # Basic style settings
        ttk::style configure . \
            -background $colors(-bg_main) \
            -foreground $colors(-fg_main) \
            -font $base_font

        # Scrollbar
        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.thumb -expand true
            }
        }

        ttk::style configure TScrollbar \
            -troughcolor $colors(-bg_main) -troughrelief flat \
            -background $colors(-scrollbar) -relief flat
        
        # Text 
        ttk::style configure TText \
            -background $colors(-bg_text) \
            -foreground $colors(-fg_text) \
            -insertbackground $colors(-fg_text) \
            -padx 16 -pady 16 \
            -borderwidth 1 -relief solid \

        ttk::style configure Title.TText \
            -foreground $colors(-fg_title) \
            -font $title_font

        # Statusbar
        ttk::style configure Statusbar.TFrame -background $colors(-bg_status)
        ttk::style configure Statusbar.TLabel -background $colors(-bg_status)
    }
}
"""

class Highlighter():
    def match_pattern(target, pattern, tag):
        # remove tag
        target.tag_remove(tag, "1.0", tk.END)

        # find and highlight all matches
        lines = target.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            for match in re.finditer(pattern, line):
                target.tag_add(tag, f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}")

    def highlight_title(target):
        Highlighter.match_pattern(target, r"#[^\n]*", "title")

class AboutDialog(tk.Toplevel):
    """Modal about dialog for idle"""
    def __init__(self, parent):
        """Create popup, do not return until tk widget destroyed."""
        super().__init__(parent)
        self.configure(borderwidth=5)
        # place dialog below parent if running htest
        self.geometry("+%d+%d" % (parent.winfo_rootx()+30, parent.winfo_rooty()+30))

        self.bg = "#bbbbbb"
        self.fg = "#000000"
        self.create_widgets()
        self.resizable(height=False, width=False)
        self.title('About')
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.ok)
        
        self.button_ok.focus_set()
        self.bind('<Return>', self.ok)  # dismiss dialog
        self.bind('<Escape>', self.ok)  # dismiss dialog
        self._current_textview = None
        
        self.deiconify()
        self.wait_window()

    def create_widgets(self):
        frame = tk.Frame(self, borderwidth=2, relief=tk.SUNKEN)
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)
        frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.button_ok = tk.Button(frame_buttons, text='Close', command=self.ok)
        self.button_ok.pack(padx=5, pady=5)

        frame_background = tk.Frame(frame, bg=self.bg)
        frame_background.pack(expand=True, fill=tk.BOTH)

        header = tk.Label(frame_background, text='Writer', fg=self.fg, bg=self.bg, font=('courier', 24, 'bold'))
        header.grid(row=0, column=0, sticky=tk.E, padx=6, pady=10)

        byline_text = "Distraction free writer app." + 5*'\n'
        byline = tk.Label(frame_background, text=byline_text, justify=tk.LEFT, fg=self.fg, bg=self.bg)
        byline.grid(row=2, column=0, sticky=tk.W, columnspan=3, padx=6, pady=5)
        github = tk.Label(frame_background, text='https://github.com/oliverjakobs/writer', justify=tk.LEFT, fg=self.fg, bg=self.bg)
        github.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=6, pady=6)


        frame = tk.Frame(frame_background, borderwidth=1, relief=tk.SUNKEN, height=2, bg=self.bg)
        frame.grid(row=8, column=0, sticky=tk.EW, columnspan=3, padx=5, pady=5)

        py_buttons = tk.Frame(frame_background, bg=self.bg)
        py_buttons.grid(row=10, column=0, columnspan=2, sticky=tk.NSEW)
        self.py_license = tk.Button(py_buttons, text='README', width=8, highlightbackground=self.bg)
        self.py_license.pack(side=tk.LEFT, padx=10, pady=10)
        self.py_copyright = tk.Button(py_buttons, text='Copyright', width=8, highlightbackground=self.bg)
        self.py_copyright.pack(side=tk.LEFT, padx=10, pady=10)
        self.py_credits = tk.Button(py_buttons, text='Credits', width=8, highlightbackground=self.bg)
        self.py_credits.pack(side=tk.LEFT, padx=10, pady=10)


    def ok(self, event=None):
        "Dismiss help_about dialog."
        self.grab_release()
        self.destroy()

class View(tk.Tk):
    def __init__(self, window_config, theme_config):
        super().__init__()

        self.geometry(f"{window_config['width']}x{window_config['height']}")
        self.state(window_config['state'])
        
        # style
        themes = ExtendendThemes()
        #themes.load_from_files(*glob(f"{theme_config['dir']}/*.tcl"))
        themes.load_from_str(BUILTIN_THEME)
        themes.theme_use('dark')

        # content
        self.load_workspace(window_config['text_width']).pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.load_statusbar().pack(side=tk.BOTTOM, fill=tk.X)

        self.load_menu()

        self._apply_style()

    def _apply_style(self):
        self.text._apply_style("TText")

        # apply style for title tag
        self.text.tag_config("title", ttk.Style().configure("Title.TText"))

    def theme_use(self, name=None):
        if name is None:
            return ttk.Style().theme_use()

        ttk.Style.theme_use(name)
        self._apply_style()

    def load_menu(self):
        menu = tk.Menu(self)

        # file
        menu_file = tk.Menu(menu, tearoff=0)
        menu_file.add_command(label="New File", accelerator="Ctrl+N", command=lambda: self.event_generate('<<new>>'))
        menu_file.add_command(label="Open File", accelerator="Ctrl+O", command=lambda: self.event_generate('<<open>>'))
        menu_file.add_separator()
        menu_file.add_command(label="Save", accelerator="Ctrl+S", command=lambda: self.event_generate('<<save>>'))
        menu_file.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=lambda: self.event_generate('<<save-as>>'))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda e: self.event_generate('<<wnd-close>>'))

        # edit
        menu_edit = tk.Menu(menu, tearoff=0)
        menu_edit.add_command(label="Undo", accelerator="Ctrl+Z", command=self.text.edit_undo)
        menu_edit.add_command(label="Redo", accelerator="Ctrl+Y", command=self.text.edit_redo)
        menu_edit.add_separator()
        menu_edit.add_command(label="Cut", accelerator="Ctrl+X")
        menu_edit.add_command(label="Copy", accelerator="Ctrl+C")
        menu_edit.add_command(label="Paste", accelerator="Ctrl+V")
        menu_edit.add_separator()
        menu_edit.add_command(label="Find", accelerator="Ctrl+F")
        menu_edit.add_command(label="Replace", accelerator="Ctrl+H")

        # help
        menu_help = tk.Menu(menu, tearoff=0)
        menu_help.add_command(label="About", command=self.about_dialog)

        menu.add_cascade(label="File", menu=menu_file)
        menu.add_cascade(label="Edit", menu=menu_edit)
        menu.add_cascade(label="Help", menu=menu_help)
        self.config(menu=menu)

    def about_dialog(self, event=None):
        "Handle Help 'About IDLE' event."
        # Synchronize with macosx.overrideRootMenu.about_dialog.
        AboutDialog(self)
        return "break"

    def load_statusbar(self):
        bar = ttk.Frame(self, style='Statusbar.TFrame')

        self.status = FadingLabel(bar, text="", style='Statusbar.TLabel')

        self.word_count = tk.StringVar(value="Wordcount: -")
        self.insert_pos = tk.StringVar(value="Ln -, Col -")

        frame = ttk.Frame(bar, style='Statusbar.TFrame')
        label_word_count = ttk.Label(frame, textvariable=self.word_count, style='Statusbar.TLabel')
        label_insert_pos = ttk.Label(frame, textvariable=self.insert_pos, style='Statusbar.TLabel')

        label_word_count.pack(side=tk.LEFT, padx=8)
        label_insert_pos.pack(side=tk.LEFT, padx=8)

        # grid
        bar.columnconfigure(1, weight=1)

        self.status.grid(row=0, column=0, sticky=tk.W, padx=8, pady=2)
        frame.grid(row=0, column=1, sticky=tk.E, padx=32, pady=2)

        return bar

    def load_workspace(self, text_width):
        workspace = ttk.Frame(self)

        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(0, weight=1)

        # text frame
        frame = ttk.Frame(workspace)
        self.text = ExtendedText(frame, wrap=tk.WORD, width=text_width, undo=True)
        self.text.pack(side=tk.TOP, fill=tk.Y, expand=True, pady=8)

        # scrollbar
        scroll = AutoScrollbar(workspace, orient=tk.VERTICAL)

        # grid
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        scroll.grid(row=0, column=1, sticky=tk.NS)

        # scroll commands
        scroll["command"] = lambda *args: self.text.yview(*args)
        self.text["yscrollcommand"] = lambda first, last: scroll.set(first, last)

        # focus on text widget
        self.text.focus_set()

        return workspace

    def write_status(self, msg):
        self.status.write(msg)

    def error_status(self, msg):
        self.status.write("[Error]: " + msg)

    def update_insert_pos(self):
        ln, col = self.text.index('insert').split('.')
        self.insert_pos.set(f"Ln {ln}, Col {col}")

    def update_word_count(self):
        count = len(re.findall('\w+', self.text.get('1.0', 'end-1c')))
        self.word_count.set(f"Wordcount: {count}")

    def update_window_config(self, config):
        if self.state() != 'zoomed':
            config['width'] = self.winfo_width()
            config['height'] = self.winfo_height()

        config['state'] = 'zoomed' if self.state() == 'zoomed' else 'normal'
        config['text_width'] = self.text.cget('width')

        return config

    def update_theme_config(self, config):
        config['name'] = self.theme_use()
        return config


class Workspace():
    def __init__(self, text):

        self.text = text
        self.saved = True
        self.set_filename(None)
    
    def set_filename(self, filename):
        self.path = os.path.abspath(filename or "")
        self.filename = os.path.basename(filename) if filename else "untitled"

    def get_title(self):
        return ("" if self.saved else "*") + self.filename

    def new_file(self):
        self.text.delete('1.0', tk.END)
        # prevent undoing clearing the text
        self.text.edit_reset()

        self.saved = True
        self.set_filename(filename)

    def read_file(self, filename) -> bool:
        try:
            with open(filename, "r") as f:
                text = f.read()
                # clear text
                self.text.delete('1.0', tk.END)
                # insert new text
                self.text.insert('1.0', text)
                # prevent undoing reading the file
                self.text.edit_reset()
        except UnicodeDecodeError as e:
            messagebox.showerror("UnicodeDecodeError", f"Could not open {filename}:\n{e}")
            return False
        except FileNotFoundError as e:
            messagebox.showerror("FileNotFoundError", f"Could not open {filename}:\n{e}")
            return False

        self.saved = True
        self.set_filename(filename)
        return True

    def write_file(self, filename) -> bool:
        try:
            with open(filename, "w") as f:
                f.write(self.text.get('1.0', 'end-1c'))
        except Exception as e:
            messagebox.showerror("Error", f"Could not save {filename}:\n{e}")
            return False

        self.saved = True
        self.set_filename(filename)
        return True
    
    def ask_save(self):
        if self.saved:
            return 'no'

        # ask if unsaved changes should be saved
        title = "Save on Close"
        prompt = f"Do you want to save changes to \"{self.filename}\"?"
        result = messagebox.askyesnocancel(title=title, message=prompt, default=messagebox.YES)

        if result is True:      # yes
            return 'yes'
        elif result is False:   # no
            return 'no'

        return 'cancel'

DEFAULT_CONFIG = {
    'window': {
        'width': 1200,
        'height': 800,
        'state': 'normal',
        'text_width': 128
    },
    'theme': {
        'dir': './themes',
        'name': 'dark'
    },
    'colors': {
        'fg_main':   '#e1e4e8',
        'bg_main':   '#454545',
        'bg_status': '#2f2f2f',
        'fg_text':   '#000000',
        'bg_text':   '#f1f1f1',
        'fg_title':  '#b392f0',
        'scrollbar': '#6f6f6f'
    }
}

FILEDIALOG_OPTIONS = {
    "defaultextension" : ".txt",
    "filetypes": [ ("All Files", "*.*") ]
}

class Writer():
    def __init__(self, config_path, filename):

        # parse config file
        config = ConfigParser(DEFAULT_CONFIG)

        config.read(config_path)

        self.window_config = {
            'width': config.getint('window', 'width'),
            'height': config.getint('window', 'height'),
            'state': config.get('window', 'state'),
            'text_width': config.getint('window', 'text_width')
        }

        self.theme_config = {
            'dir': config.get('theme', 'dir'),
            'name': config.get('theme', 'name')
        }

        self.config_path = config_path

        # setup
        self.view = View(self.window_config, self.theme_config)
        self.workspace = Workspace(self.view.text)

        # bind events (binding to text widgets to prevent text specific events)
        self.view.bind_class('Text', "<Control-n>", self.new_file)
        self.view.bind_class('Text', "<Control-o>", self.open)
        self.view.bind_class('Text', "<Control-s>", self.save)
        self.view.bind_class('Text', "<Control-S>", self.save_as)

        self.view.bind("<<text-changed>>", self.on_text_change)
        self.view.bind("<<insert-moved>>", self.on_insert_move)

        self.view.bind('<<new>>', self.new_file)
        self.view.bind('<<open>>', self.open)
        self.view.bind('<<save>>', self.save)
        self.view.bind('<<save-as>>', self.save_as)
        self.view.bind('<<wnd-close>>', self.exit)

        self.view.protocol("WM_DELETE_WINDOW", self.exit)

        # read file
        if filename:
            self.workspace.read_file(filename)

        self.update_title()

    def run(self):
        self.view.mainloop()

    def on_text_change(self, event):
        self.view.update_word_count()
        Highlighter.highlight_title(self.view.text)

        if self.workspace.saved:
            self.workspace.saved = False
            self.update_title()

    def on_insert_move(self, event):
        self.view.update_insert_pos()

    def update_title(self):
        self.view.title(self.workspace.get_title())

    def new_file(self, event=None):
        self.workspace.new_file()
        self.update_title()

    def open(self, event=None, filename=None) -> bool:
        path = filename or filedialog.askopenfilename(**FILEDIALOG_OPTIONS)
        if not path:
            return False

        result = self.workspace.read_file(path)
        if result:
            self.view.write_status(f"Opened {path}")
        else:
            self.view.error_status(f"Failed to open {path}")

        self.update_title()
        return result

    def save(self, event=None):
        return self.save_as(event=event, filename=self.workspace.path)

    def save_as(self, event=None, filename=None) -> bool:
        path = filename or filedialog.asksaveasfilename(**FILEDIALOG_OPTIONS)
        if not path:
            return False

        result = self.workspace.write_file(path)
        if result:
            self.view.write_status(f"Successfully saved {path}")
        else:
            self.view.error_status(f"Failed to save {path}")

        self.update_title()
        return result

    def exit(self, *args):

        # save config
        config = ConfigParser()
        config['window'] = self.view.update_window_config(self.window_config)
        config['theme'] = self.view.update_theme_config(self.theme_config)

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

        result = self.workspace.ask_save()
        if (result == 'yes' and self.save()) or result == 'no':
            self.view.destroy()

#TODO: custom titlebar
#TODO: style, font selector popup
if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = Writer("config.ini", filename)
    app.run()

