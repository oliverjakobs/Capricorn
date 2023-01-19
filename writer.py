import os, sys, re
from configparser import ConfigParser

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
    def match_pattern(target: tk.Text, pattern: str, tag: str) -> None:
        # remove tag
        target.tag_remove(tag, "1.0", tk.END)

        # find and highlight all matches
        lines = target.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            for match in re.finditer(pattern, line):
                target.tag_add(tag, f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}")

    def highlight_title(target: tk.Text) -> None:
        Highlighter.match_pattern(target, r"#[^\n]*", "title")

class AboutDialog(tk.Toplevel):
    """Modal about dialog for idle"""
    def __init__(self, parent):
        """Create popup, do not return until tk widget destroyed."""
        super().__init__(parent)
        self.configure(borderwidth=5)
        # place dialog below parent if running htest
        self.geometry("+%d+%d" % (parent.winfo_rootx()+30, parent.winfo_rooty()+30))

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

        header = tk.Label(frame_content, text='Writer', fg=fg, bg=bg, font=('courier', 24, 'bold'))
        header.grid(row=0, column=0, sticky=tk.W, padx=6, pady=10)

        byline_text = "Distraction free writer app." + (5 * '\n')
        byline = tk.Label(frame_content, text=byline_text, fg=fg, bg=bg)
        byline.grid(row=1, column=0, sticky=tk.W, padx=6, pady=5)
        github = tk.Label(frame_content, text='https://github.com/oliverjakobs/writer', fg=fg, bg=bg)
        github.grid(row=2, column=0, sticky=tk.W, padx=6, pady=6)

        separator = ttk.Separator(frame_content, orient=tk.HORIZONTAL)
        separator.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)

        # buttons
        frame_buttons = tk.Frame(frame_content, bg=bg)

        self.btn_readme = tk.Button(frame_buttons, text='README', width=8, highlightbackground=bg)
        self.btn_readme.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_copyright = tk.Button(frame_buttons, text='Copyright', width=8, highlightbackground=bg)
        self.btn_copyright.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_credits = tk.Button(frame_buttons, text='Credits', width=8, highlightbackground=bg)
        self.btn_credits.pack(side=tk.LEFT, padx=10, pady=10)

        frame_buttons.grid(row=4, column=0, sticky=tk.NSEW)

        # footer
        frame_footer = tk.Frame(self)

        self.button_ok = tk.Button(frame_footer, text='Close', padx=6, command=self.ok)
        self.button_ok.pack(padx=5, pady=5)

        frame_content.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        frame_footer.pack(side=tk.BOTTOM, fill=tk.X)


    def ok(self, event=None):
        "Dismiss help_about dialog."
        self.grab_release()
        self.destroy()

class View(tk.Tk):
    def __init__(self, config):
        super().__init__()

        self.geometry(f"{config['width']}x{config['height']}")
        self.state(config['state'])
        
        # style
        themes = ExtendendThemes()
        #themes.load_from_files(*glob(f"{theme_config['dir']}/*.tcl"))
        themes.load_from_str(BUILTIN_THEME)
        themes.theme_use('dark')

        # content
        self.load_workspace().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.load_statusbar().pack(side=tk.BOTTOM, fill=tk.X)

        self.load_menu()

        # bind events (binding to text widget to override text specific events)
        self.text.bind('<Control-n>', self.on_new)
        self.text.bind('<Control-o>', self.on_open)
        self.text.bind('<Control-s>', self.on_save)
        self.text.bind('<Control-S>', self.on_save_as)

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
        menu_file.add_command(label="New File", accelerator="Ctrl+N", command=self.on_new)
        menu_file.add_command(label="Open File", accelerator="Ctrl+O", command=self.on_open)
        menu_file.add_separator()
        menu_file.add_command(label="Save", accelerator="Ctrl+S", command=self.on_save)
        menu_file.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.on_save_as)
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

    def on_new(self, event=None):
        self.event_generate('<<new>>')
        return 'break'

    def on_open(self, event=None):
        self.event_generate('<<open>>')
        return 'break'

    def on_save(self, event=None):
        self.event_generate('<<save>>')
        return 'break'

    def on_save_as(self, event=None):
        self.event_generate('<<save-as>>')
        return 'break'

    def about_dialog(self, event=None):
        AboutDialog(self)
        return 'break'

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

    def load_workspace(self,):
        workspace = ttk.Frame(self)

        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(0, weight=1)

        # text frame
        frame = ttk.Frame(workspace)
        self.text = ExtendedText(frame, wrap=tk.WORD, undo=True)
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

    def get_config(self, config):
        if self.state() != 'zoomed':
            config['width'] = self.winfo_width()
            config['height'] = self.winfo_height()

        config['state'] = 'zoomed' if self.state() == 'zoomed' else 'normal'

        return config


class Workspace():
    def __init__(self, config, text):

        self.text = text
        self.text.configure(width=config['text_width'])

        self.saved = True
        self.set_filename(None)

    def set_filename(self, filename):
        self.path = os.path.abspath(filename) if filename else None
        self.filename = os.path.basename(filename) if filename else "untitled"

    def get_title(self):
        return ("" if self.saved else "*") + self.filename

    def set_unsaved(self):
        was_saved = self.saved
        self.saved = False
        return was_saved

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
        ...
    
    def get_config(self, config):
        config['last_file'] = self.path or ""
        config['text_width'] = self.text.cget('width')
        return config

DEFAULT_CONFIG = {
    'view': {
        'width': '1200',
        'height': '800',
        'state': 'normal'
    },
    'workspace': {
        'text_width': '128',
        'last_file': ''
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
        config = ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        config.read(config_path)

        self.view_config = dict(config['view'])
        self.ws_config = dict(config['workspace'])

        self.config_path = config_path

        #view
        self.view = View(self.view_config)

        # workspace
        self.workspace = Workspace(self.ws_config, self.view.text)

        # bind events
        self.view.bind("<<text-changed>>", self.on_text_change)
        self.view.bind("<<insert-moved>>", self.on_insert_move)

        self.view.bind('<<new>>', self.new_file)
        self.view.bind('<<open>>', self.open)
        self.view.bind('<<save>>', self.save)
        self.view.bind('<<save-as>>', self.save_as)
        self.view.bind('<<wnd-close>>', self.exit)

        self.view.protocol("WM_DELETE_WINDOW", self.exit)

        # read file
        path = filename or self.ws_config['last_file']
        if path:
            self.workspace.read_file(path)

        self.update_title()

    def run(self):
        self.view.mainloop()

    def on_text_change(self, event):
        self.view.update_word_count()
        Highlighter.highlight_title(self.view.text)

        if self.workspace.set_unsaved():
            self.update_title()

    def on_insert_move(self, event):
        self.view.update_insert_pos()

    def update_title(self):
        self.view.title(self.workspace.get_title())

    def check_saved(self):
        """ Check if the file is saved and can be closed. 
            Returns True if it can be closed, esle False  """
        
        if self.workspace.saved:
            return True

        # ask if unsaved changes should be saved
        title = "Save on Close"
        prompt = f"Do you want to save changes to \"{self.workspace.filename}\"?"
        result = messagebox.askyesnocancel(title=title, message=prompt, default=messagebox.YES)

        if result is True:      # yes
            return self.save()
        elif result is False:   # no
            return True

        return False            # cancel

    def new_file(self, event=None) -> bool:
        if not self.check_saved():
            return False

        self.workspace.new_file()
        self.update_title()
        return True

    def open(self, event=None, filename=None) -> bool:
        if not self.check_saved():
            return False

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
        config['view'] = self.view.get_config(self.view_config)
        config['workspace'] = self.workspace.get_config(self.ws_config)

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

        if self.check_saved():
            self.view.destroy()

#TODO: custom titlebar
#TODO: style, font selector popup
if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = Writer("config.ini", filename)
    app.run()

