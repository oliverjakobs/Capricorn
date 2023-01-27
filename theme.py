"""IDLE Configuration Dialog: support user customization of IDLE by GUI

Customize font faces, sizes, and colorization attributes.  Set indentation
defaults.  Customize keybindings.  Colorization and keybindings can be
saved as user defined sets.  Select startup options including shell/editor
and default window size.  Define additional help sources.

Note that tab width in IDLE is currently fixed at eight due to Tk issues.
Refer to comments in EditorWindow autoindent code for details.

"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from lib.extendedTk import DigitEntry
from lib.autocomplete import AutocompleteCombobox


class ConfigDialog(tk.Toplevel):
    """Config dialog for IDLE. """

    def __init__(self, parent, title=''):
        """Show the tabbed dialog for user configuration. """
        super().__init__(parent)
        self.withdraw()

        self.title(title or 'IDLE Preferences')
        x = parent.winfo_rootx() + 20
        y = parent.winfo_rooty() + 30
        self.geometry(f'+{x}+{y}')
        
        self.create_widgets()
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.grab_set()
        self.wm_deiconify()
        self.wait_window()

    def create_widgets(self):

        # notebook
        self.note = ttk.Notebook(self, padding=(4, 6, 4, 0))
        self.note.enable_traversal()

        self.note.add(GeneralPage(self.note), text='General')
        self.note.add(ColorPage(self.note), text='Colors')
        
        self.note.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        
        # buttons
        frame_btns = ttk.Frame(self)

        ttk.Button(frame_btns, text='Ok', command=self.ok, takefocus=False).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text='Apply', command=self.apply, takefocus=False).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text='Cancel', command=self.cancel, takefocus=False).pack(side=tk.LEFT, padx=5)

        frame_btns.pack(side=tk.BOTTOM, pady=6)

    def ok(self):
        """Apply config changes, then dismiss dialog. """
        self.apply()
        self.destroy()

    def apply(self):
        """Apply config changes and leave dialog open. """

    def cancel(self):
        """Dismiss config dialog. """
        # changes.clear()
        self.destroy()

    def destroy(self):
        self.grab_release()
        super().destroy()



# class TabPage(Frame):  # A template for Page classes.
#     def __init__(self, master):
#         super().__init__(master)
#         self.create_page_tab()
#         self.load_tab_cfg()
#     def create_page_tab(self):
#         # Define tk vars and register var and callback with tracers.
#         # Create subframes and widgets.
#         # Pack widgets.
#     def load_tab_cfg(self):
#         # Initialize widgets with data from idleConf.
#     def var_changed_var_name():
#         # For each tk var that needs other than default callback.
#     def other_methods():
#         # Define tab-specific behavior.

class ColorPage(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)

        self.config = {
            'fg_main':   tk.StringVar(self, '#e1e4e8'),
            'bg_main':   tk.StringVar(self, '#454545'),
            'bg_status': tk.StringVar(self, '#2f2f2f'),
            'fg_text':   tk.StringVar(self, '#000000'),
            'bg_text':   tk.StringVar(self, '#f1f1f1'),
            'fg_title':  tk.StringVar(self, '#a968c2'),
            'scrollbar': tk.StringVar(self, '#6f6f6f')
        }

        self.create_page_highlight()
        self.load_theme_cfg()

    def create_page_highlight(self):
        self.columnconfigure(0, weight=1)

        row = 0
        for color in self.config:
            label_color = ttk.Label(self, text=color)
            entry_color = ttk.Entry(self, width=8, textvariable=self.config[color])

            label_color.grid(row=row, column=0, sticky=tk.W, padx=5, pady=4)
            entry_color.grid(row=row, column=1, sticky=tk.E, padx=10, pady=4)

            row += 1



    def load_theme_cfg(self):
        """Load current configuration settings for the theme options. """


class GeneralPage(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)

        self.config_font = {
            'Family': tk.StringVar(self, 'Courier New'),
            'Size': tk.IntVar(self, 10),
            'Title Size': tk.IntVar(self, 24),
            'Separator Size': tk.IntVar(self, 16)
        }

        self.create_frame_workspace()
        self.create_frame_fonts()
        self.load_general_cfg()

    def create_frame_workspace(self):
        self.text_width = tk.StringVar(self)

        frame_workspace = ttk.LabelFrame(self, borderwidth=2, relief=tk.GROOVE, text="Workspace Preferences")

        frame_workspace.columnconfigure(0, weight=1)

        text_width_title = ttk.Label(frame_workspace, text='Text Width (in characters)')
        self.text_width_int = DigitEntry(frame_workspace, justify=tk.RIGHT, width=8, textvariable=self.text_width)
        
        text_width_title.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.text_width_int.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        frame_workspace.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)

    def create_frame_fonts(self):
        frame_fonts = ttk.LabelFrame(self, borderwidth=2, relief=tk.GROOVE, text="Font Preferences")

        frame_fonts.columnconfigure(0, weight=1)
        
        # font family
        label_font_family = ttk.Label(frame_fonts, text='Family')
        entry_font_family = AutocompleteCombobox(frame_fonts, textvariable=self.config_font['Family'])

        font_names = sorted(set(tkfont.families(self)))
        entry_font_family.set_completion_list(font_names)

        label_font_family.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_font_family.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        # font sizes
        row = 1
        for name, var in list(self.config_font.items())[1:]:
            label = ttk.Label(frame_fonts, text=name)
            entry = DigitEntry(frame_fonts, justify=tk.RIGHT, width=8, textvariable=var)

            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry.grid(row=row, column=1, sticky=tk.E, padx=10, pady=5)

            row += 1

        frame_fonts.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)


    def load_general_cfg(self):
        "Load current configuration settings for the general options."



        


import tkinter as tk



if __name__ == '__main__':
    root = tk.Tk()
    dialog = ConfigDialog(root)

    dialog.mainloop()
