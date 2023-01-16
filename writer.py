import os, sys, re
from configparser import ConfigParser

# import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# import own stuff
from extendedTk import *

class Statusbar(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master, style='Statusbar.TFrame')

        self.status = FadingLabel(self, text="", style='Statusbar.TLabel')

        self.word_count = tk.StringVar(value="Wordcount: -")
        self.insert_pos = tk.StringVar(value="Ln -, Col -")

        frame = ttk.Frame(self, style='Statusbar.TFrame')
        label_word_count = ttk.Label(frame, textvariable=self.word_count, style='Statusbar.TLabel')
        label_insert_pos = ttk.Label(frame, textvariable=self.insert_pos, style='Statusbar.TLabel')

        label_word_count.pack(side=tk.LEFT, padx=8)
        label_insert_pos.pack(side=tk.LEFT, padx=8)

        # grid
        self.columnconfigure(1, weight=1)

        self.status.grid(row=0, column=0, sticky=tk.W, padx=8, pady=2)
        frame.grid(row=0, column=1, sticky=tk.E, padx=32, pady=2)

        # events
        self.bind("<<TextChange>>", lambda e: print("text change"))

    def write(self, msg):
        self.status.write(msg)

    def error(self, msg):
        self.status.write("[Error]: " + msg)

    def update_insert_pos(self, event):
        ln, col = event.widget.index('insert').split('.')
        self.insert_pos.set(f"Ln {ln}, Col {col}")

    def update_word_count(self, event):
        count = len(re.findall('\w+', event.widget.get('1.0', 'end-1c')))
        self.word_count.set(f"Wordcount: {count}")

class Highlighter():
    def match_pattern(target, pattern, tag):
        """ Removes all highlights and highlights all matches of the pattern. """

        # remove tag
        target.tag_remove(tag, "1.0", tk.END)

        # find and highlight all matches
        lines = target.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            for match in re.finditer(pattern, line):
                target.tag_add(tag, f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}")

class Workspace(ttk.Frame):
    def __init__(self, master, text_width):
        super().__init__(master)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # text frame
        frame = ttk.Frame(self)
        self.text = ExtendedText(frame, wrap=tk.WORD, width=text_width, undo=True)
        self.text.pack(side=tk.TOP, fill=tk.Y, expand=True, pady=8)

        # scrollbar
        self.scroll = AutoScrollbar(self, orient=tk.VERTICAL)

        # grid
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.scroll.grid(row=0, column=1, sticky=tk.NS)

        # scroll commands
        self.scroll["command"] = lambda *args: self.text.yview(*args)
        self.text["yscrollcommand"] = lambda first, last: self.scroll.set(first, last)

        self._apply_style()
        
        # focus on text widget
        self.text.focus_set()

    def clear_text(self):
        self.text.delete('1.0', tk.END)
        # prevent undoing clearing the text
        self.text.edit_reset()

    def set_content(self, text):
        # clear text
        self.text.delete('1.0', tk.END)
        # insert new text
        self.text.insert('1.0', text)
        # prevent undoing reading the file
        self.text.edit_reset()

    def get_content(self):
        return self.text.get('1.0', 'end-1c')

    def undo(self) -> None:
        self.text.edit_undo()

    def redo(self) -> None:
        self.text.edit_redo()

    def hightlight_title(self):
        Highlighter.match_pattern(self.text, r"#[^\n]*", "title")

    def get_text_width(self):
        return self.text.cget('width')

    def _apply_style(self):
        self.text._apply_style("TText")

        # apply style for title tag
        self.text.tag_config("title", ttk.Style().configure("Title.TText"))
    

class Writer(tk.Tk):
    def __init__(self, config_path):
        super().__init__()

        # parse config file
        config = ConfigParser()
        config.read(config_path)

        self.theme_config = {
            'dir': config.get('theme', 'dir', fallback=None),
            'name': config.get('theme', 'name', fallback=None)
        }

        self.window_config = {
            'width': config.getint('window', 'width', fallback=1200),
            'height': config.getint('window', 'height', fallback=800),
            'state': config.get('window', 'state', fallback='normal'),
            'text_width': config.getint('window', 'text_width', fallback=128)
        }

        self.config_path = config_path

        # setup
        self.geometry(f"{self.window_config['width']}x{self.window_config['height']}")
        self.state(self.window_config['state'])

        self._filedialog_options = { "defaultextension" : ".txt", "filetypes": [ ("All Files", "*.*") ] }

        # style
        style = ttk.Style()
        self.theme_names = load_themes(style, self.theme_config['dir'])

        style.theme_use(self.theme_config['name'])
        self.theme_var = tk.StringVar(self, style.theme_use())

        # workspace
        self.workspace = Workspace(self, self.window_config['text_width'])

        # status bar
        self.statusbar = Statusbar(self)

        self.workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # bind events (binding to text widgets to prevent text specific events)
        self.bind_class('Text', "<Control-n>", self.new_file)
        self.bind_class('Text', "<Control-o>", self.open)
        self.bind_class('Text', "<Control-s>", self.save)
        self.bind_class('Text', "<Control-S>", self.save_as)

        self.bind("<<InsertMove>>", self.statusbar.update_insert_pos)
        self.bind("<<TextChange>>", self.on_text_change)

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.saved = True
        self.set_filename(None)
        self.update_title()

    def theme_use(self, name=None):
        if name is None:
            return ttk.Style().theme_use()

        ttk.Style.theme_use(name)
        self.workspace._apply_style()

    def on_text_change(self, event):
        self.statusbar.update_word_count(event)
        self.workspace.hightlight_title()

        if self.saved:
            self.saved = False
            self.update_title()

    def load_menu(self):
        menu = tk.Menu(self)

        # file
        menu_file = tk.Menu(menu, tearoff=0)
        menu_file.add_command(label="New File", accelerator="Ctrl+N", command=self.new_file)
        menu_file.add_command(label="Open File", accelerator="Ctrl+O", command=self.open)
        menu_file.add_separator()
        menu_file.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
        menu_file.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.save_as)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.exit)

        # edit
        menu_edit = tk.Menu(menu, tearoff=0)
        menu_edit.add_command(label="Undo", accelerator="Ctrl+Z", command=self.workspace.undo)
        menu_edit.add_command(label="Redo", accelerator="Ctrl+Y", command=self.workspace.redo)
        menu_edit.add_separator()
        menu_edit.add_command(label="Cut", accelerator="Ctrl+X")
        menu_edit.add_command(label="Copy", accelerator="Ctrl+C")
        menu_edit.add_command(label="Paste", accelerator="Ctrl+V")
        menu_edit.add_separator()
        menu_edit.add_command(label="Find", accelerator="Ctrl+F")
        menu_edit.add_command(label="Replace", accelerator="Ctrl+H")

        # view
        menu_view = tk.Menu(menu, tearoff=0)

        menu_themes = tk.Menu(menu_view, tearoff=0)

        for theme in self.theme_names:
            menu_themes.add_radiobutton(label=theme, value=theme, variable=self.theme_var,
                command=lambda: self.theme_use(self.theme_var.get()))

        menu_view.add_cascade(label="Themes", menu=menu_themes)

        # help
        menu_help = tk.Menu(menu, tearoff=0)
        menu_help.add_command(label="About")

        menu.add_cascade(label="File", menu=menu_file)
        menu.add_cascade(label="Edit", menu=menu_edit)
        menu.add_cascade(label="View", menu=menu_view)
        menu.add_cascade(label="Help", menu=menu_help)
        self.config(menu=menu)

    def set_filename(self, filename):
        self.path = os.path.abspath(filename or "")
        self.filename = os.path.basename(filename) if filename else "untitled"

    def update_title(self):
        self.title(self.filename if self.saved else "*" + self.filename)

    def read_file(self, filename) -> bool:
        try:
            with open(filename, "r") as f:
                self.workspace.set_content(f.read())
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
                f.write(self.workspace.get_content())
        except Exception as e:
            messagebox.showerror("Error", f"Could not save {filename}:\n{e}")
            return False

        self.saved = True
        self.set_filename(filename)
        return True

    def new_file(self, event=None):
        self.workspace.clear_text()
        self.saved = True
        self.set_filename(None)

        self.update_title()

    def open(self, event=None, filename=None) -> bool:
        path = filename or filedialog.askopenfilename(**self._filedialog_options)
        if not path:
            return

        if self.read_file(path):
            self.statusbar.write(f"Opened {path}")
        else:
            self.statusbar.error(f"Failed to open {path}")

        self.update_title()

    def save(self, event=None):
        return self.save_as(event=event, filename=self.path)

    def save_as(self, event=None, filename=None) -> bool:
        path = filename or filedialog.asksaveasfilename(**self._filedialog_options)
        if not path:
            return

        if self.write_file(path):
            self.statusbar.write(f"Successfully saved {path}")
        else:
            self.statusbar.error(f"Failed to save {path}")

        self.update_title()

    def update_window_config(self):
        if self.state() != 'zoomed':
            self.window_config['width'] = self.winfo_width()
            self.window_config['height'] = self.winfo_height()

        self.window_config['state'] = 'zoomed' if self.state() == 'zoomed' else 'normal'
        self.window_config['text_width'] = self.workspace.get_text_width()

        return self.window_config

    def update_theme_config(self):
        self.theme_config['name'] = self.theme_use()
        return self.theme_config

    def should_close(self):
        if self.saved:
            return True

        # ask if unsaved changes should be saved
        title = "Save on Close"
        prompt = f"Do you want to save changes to \"{self.filename}\"?"
        result = messagebox.askyesnocancel(title=title, message=prompt, default=messagebox.YES, parent=self)

        if result and self.save():  # yes
            return True
        elif result is False:       # no
            return True

        return False

    def exit(self, *args):

        # save config
        config = ConfigParser()
        config['window'] = self.update_window_config()
        config['theme'] = self.update_theme_config()

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

        if self.should_close():
            self.destroy()



if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = Writer("config.ini")

    # menubar
    app.load_menu()

    # read file
    app.open(filename=filename)

    app.mainloop()

