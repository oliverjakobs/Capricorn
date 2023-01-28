import re

import tkinter as tk
from tkinter import ttk

from lib.extendedTk import *

THEME_SETTINGS = """
namespace eval ttk::theme::capricorn {
    ttk::style theme settings capricorn {
        # Basic style settings
        ttk::style configure . \
            -background $colors(-bg_main) \
            -foreground $colors(-fg_main) \
            -font $fonts(-main)

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
            -font $fonts(-title)

        ttk::style configure Separator.TText \
            -justify center \
            -spacing1 12 -spacing3 12 \
            -font $fonts(-separator)

        # Statusbar
        ttk::style configure Statusbar.TFrame -background $colors(-bg_status)
        ttk::style configure Statusbar.TLabel -background $colors(-bg_status)
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
        self.load_workspace().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.load_statusbar().pack(side=tk.BOTTOM, fill=tk.X)

        self.load_menu()

        # create and use theme
        self.tk.eval("""
        namespace eval ttk::theme::capricorn {
            ttk::style theme create capricorn -parent default
        }
        """)
        ttk.Style().theme_use('capricorn')

        # bind events (binding to text widget to override text specific events)
        self.text.bind('<Control-n>', self.on_new)
        self.text.bind('<Control-o>', self.on_open)
        self.text.bind('<Control-s>', self.on_save)
        self.text.bind('<Control-S>', self.on_save_as)

    def _apply_style(self):
        self.text._apply_style("TText")

        # apply style for tags
        self.text.tag_config("title", ttk.Style().configure("Title.TText"))
        self.text.tag_config("separator", ttk.Style().configure("Separator.TText"))

    def load_config(self, config, colors, fonts):
        self.geometry(f"{config['width']}x{config['height']}")
        self.state(config['state'])

        self.load_theme(colors, fonts)

    def load_theme(self, colors, fonts):
        # set colors
        self.tk.eval(f""" 
        namespace eval ttk::theme::capricorn {{
            array set colors {{
                -fg_main    "{colors['fg_main']}"
                -bg_main    "{colors['bg_main']}"
                -bg_status  "{colors['bg_status']}"
                -fg_text    "{colors['fg_text']}"
                -bg_text    "{colors['bg_text']}"
                -fg_title   "{colors['fg_title']}"
                -scrollbar  "{colors['scrollbar']}"
            }}
        }}
        """)

        # set fonts
        self.tk.eval(f"""
        namespace eval ttk::theme::capricorn {{
            array set fonts {{
                -main       {{ {fonts['main']} }}
                -title      {{ {fonts['title']} }}
                -separator  {{ {fonts['separator']} }}
            }}
        }}
        """)

        # apply theme settings
        self.tk.eval(THEME_SETTINGS)

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
        menu_file.add_command(label="Settings", command=lambda: self.event_generate('<<show-settings>>'))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda: self.event_generate('<<wnd-close>>'))

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
        menu_help.add_command(label="About", command=lambda: self.event_generate('<<show-about>>'))

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

    def load_statusbar(self):
        bar = ttk.Frame(self, style='Statusbar.TFrame')

        self.status = FadingLabel(bar, text="", style='Statusbar.TLabel')

        frame = ttk.Frame(bar, style='Statusbar.TFrame')
        self.label_word_count = ttk.Label(frame, style='Statusbar.TLabel')
        self.label_insert_pos = ttk.Label(frame, style='Statusbar.TLabel')

        self.label_word_count.pack(side=tk.LEFT, padx=8)
        self.label_insert_pos.pack(side=tk.LEFT, padx=8)

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
        scroll['command'] = lambda *args: self.text.yview(*args)
        self.text['yscrollcommand'] = lambda first, last: scroll.set(first, last)

        # focus on text widget
        self.text.focus_set()

        return workspace

    def write_status(self, msg):
        self.status.write(msg)

    def error_status(self, msg):
        self.status.write("[Error]: " + msg)

    def zoomed(self):
        return self.state() == 'zoomed'