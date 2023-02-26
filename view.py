import tkinter as tk
from tkinter import ttk

from lib.extendedTk import *

THEME_SETTINGS = """
namespace eval ttk::theme::capricorn {
    ttk::style theme settings capricorn {
        # Basic style settings
        ttk::style configure . \
            -background $colors(-bg_main) \
            -foreground $colors(-fg_main)

        # Entry
        ttk::style configure TEntry -fieldbackground $colors(-bg_main)
        option add *TEntry.font TkFixedFont

        # Combobox
        ttk::style configure TCombobox -fieldbackground $colors(-bg_main)
        option add *TCombobox*Listbox.background $colors(-bg_main)
        option add *TCombobox*Listbox.foreground $colors(-fg_main)

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
        ttk::style configure Text \
            -background $colors(-bg_text) \
            -foreground $colors(-fg_text) \
            -insertbackground $colors(-fg_text) \
            -padx 16 -pady 16 \
            -borderwidth 1 -relief solid \

        # Statusbar
        ttk::style configure Statusbar.TFrame -background $colors(-bg_status)
        ttk::style configure Statusbar.TLabel -background $colors(-bg_status)

        # Button
        ttk::style configure TButton \
            -padding {8 4 8 4} -anchor center \
            -background $colors(-bg_status)

        # Labelframe
        ttk::style configure TLabelframe \
            -borderwidth 1 -relief solid
    }
}
"""

#============================================================================
# view
#============================================================================
class View(tk.Tk):
    def __init__(self):
        super().__init__()
        # icon
        try:    self.iconbitmap('capricorn.ico')
        except: pass

        # content
        self.create_workspace()
        self.create_statusbar()
        self.create_menu()

        # create and use theme
        self.tk.eval("""
        namespace eval ttk::theme::capricorn {
            ttk::style theme create capricorn -parent default
        }
        """)
        ttk.Style().theme_use('capricorn')

        # bind events (binding to text widget to override text specific events)
        self.text.bind('<Control-n>', lambda e: self.on_event('<<new>>'))
        self.text.bind('<Control-o>', lambda e: self.on_event('<<open>>'))
        self.text.bind('<Control-s>', lambda e: self.on_event('<<save>>'))
        self.text.bind('<Control-S>', lambda e: self.on_event('<<save-as>>'))

    def load_config(self, config):
        self.geometry(f"{config['width']}x{config['height']}")
        self.state(config['state'])

    def load_theme(self, colors, tags):
        # set colors
        color_str = " ".join(['-%s "%s"' % (c, colors[c]) for c in colors])
        self.tk.eval("namespace eval ttk::theme::capricorn {array set colors {%s}}" % color_str)

        # apply theme settings
        self.tk.eval(THEME_SETTINGS)

        # configure tags
        for tag, settings in tags.items():
            self.text.tag_configure(tag, settings)

        # apply style for text widget
        self.text._apply_style("Text")

    def on_event(self, sequence: str):
        self.event_generate(sequence)
        return 'break'

    def create_menu(self):
        menu = ExtendedMenu(self)

        # file
        menu.load_cascade("File", [
            ("New File",  "Ctrl+N",       lambda: self.on_event('<<new>>')),
            ("Open File", "Ctrl+O",       lambda: self.on_event('<<open>>')),
            ("Save",      "Ctrl+S",       lambda: self.on_event('<<save>>')),
            ("Save As",   "Ctrl+Shift+S", lambda: self.on_event('<<save-as>>')),
            (),
            ("Settings",  None,           lambda: self.on_event('<<show-pref>>')),
            (),
            ("Exit",      None,           lambda: self.on_event('<<wnd-close>>')),
        ])

        # edit
        menu.load_cascade("Edit", [
            ("Undo",    "Ctrl+Z",   self.text.edit_undo),
            ("Redo",    "Ctrl+Y",   self.text.edit_redo),
            #(),
            #("Cut",     "Ctrl+X",   None),
            #("Copy",    "Ctrl+C",   None),
            #("Paste",   "Ctrl+V",   None),
            #(),
            #("Find",    "Ctrl+F",   None),
            #("Replace", "Ctrl+H",   None),
        ])

        # help
        menu.load_cascade("Help", [
            ("About", None, lambda: self.on_event('<<show-about>>'))
        ])

        self.config(menu=menu)

    def create_workspace(self):
        workspace = ttk.Frame(self)
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(0, weight=1)

        # text frame
        frame = ttk.Frame(workspace)

        self.text = ExtendedText(frame, wrap=tk.WORD, undo=True)
        self.text.pack(side=tk.TOP, fill=tk.Y, expand=True, pady=8)

        frame.grid(row=0, column=0, sticky=tk.NSEW)

        # scrollbar
        scroll = AutoScrollbar(workspace, orient=tk.VERTICAL)
        scroll.grid(row=0, column=1, sticky=tk.NS)

        # scroll commands
        scroll['command'] = lambda *args: self.text.yview(*args)
        self.text['yscrollcommand'] = lambda first, last: scroll.set(first, last)

        # focus on text widget
        self.text.focus_set()

        workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_statusbar(self):
        statusbar = ttk.Frame(self, style='Statusbar.TFrame')
        statusbar.columnconfigure(1, weight=1)

        self.status = FadingLabel(statusbar, text="", style='Statusbar.TLabel')
        self.status.grid(row=0, column=0, sticky=tk.W, padx=8, pady=2)

        frame = ttk.Frame(statusbar, style='Statusbar.TFrame')

        self.label_word_count = ttk.Label(frame, style='Statusbar.TLabel')
        self.label_word_count.pack(side=tk.LEFT, padx=8)

        self.label_insert_pos = ttk.Label(frame, style='Statusbar.TLabel')
        self.label_insert_pos.pack(side=tk.LEFT, padx=8)

        frame.grid(row=0, column=1, sticky=tk.E, padx=32, pady=2)

        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def write_status(self, msg):
        self.status.write(msg)

    def write_error(self, msg):
        self.status.write("[Error]: " + msg)

    def zoomed(self):
        return self.state() == 'zoomed'