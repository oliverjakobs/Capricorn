"""IDLE Configuration Dialog: support user customization of IDLE by GUI

Customize font faces, sizes, and colorization attributes.  Set indentation
defaults.  Customize keybindings.  Colorization and keybindings can be
saved as user defined sets.  Select startup options including shell/editor
and default window size.  Define additional help sources.

Note that tab width in IDLE is currently fixed at eight due to Tk issues.
Refer to comments in EditorWindow autoindent code for details.

"""
import re

from tkinter import (Toplevel, Listbox, Scale, Canvas,
                     StringVar, BooleanVar, IntVar, TRUE, FALSE,
                     TOP, BOTTOM, RIGHT, LEFT, SOLID, GROOVE,
                     NONE, BOTH, X, Y, W, E, EW, NS, NSEW, NW,
                     HORIZONTAL, VERTICAL, ANCHOR, ACTIVE, END)
from tkinter.ttk import (Frame, LabelFrame, Button, Checkbutton, Entry, Label,
                         OptionMenu, Notebook, Radiobutton, Scrollbar, Style)
from tkinter import colorchooser
import tkinter.font as tkfont
from tkinter import messagebox

from idlelib.config import idleConf, ConfigChanges
from idlelib.config_key import GetKeysDialog
from idlelib.dynoption import DynOptionMenu
from idlelib import macosx
from idlelib.query import SectionName, HelpSource
from idlelib.textview import view_text
from idlelib.autocomplete import AutoComplete
from idlelib.codecontext import CodeContext
from idlelib.parenmatch import ParenMatch
from idlelib.format import FormatParagraph
from idlelib.squeezer import Squeezer
from idlelib.textview import ScrollableTextFrame

changes = ConfigChanges()
# Reload changed options in the following classes.
reloadables = (AutoComplete, CodeContext, ParenMatch, FormatParagraph,
               Squeezer)


class ConfigDialog(Toplevel):
    """Config dialog for IDLE. """

    def __init__(self, parent, title=''):
        """Show the tabbed dialog for user configuration. """
        Toplevel.__init__(self, parent)
        self.withdraw()

        self.title(title or 'IDLE Preferences')
        x = parent.winfo_rootx() + 20
        y = parent.winfo_rooty() + 30
        self.geometry(f'+{x}+{y}')
        # Each theme element key is its display name.
        # The first value of the tuple is the sample area tag name.
        # The second value is the display name list sort index.
        self.create_widgets()
        self.resizable(height=FALSE, width=FALSE)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        #self.fontpage.fontlist.focus_set()
        # XXX Decide whether to keep or delete these key bindings.
        # Key bindings for this dialog.
        # self.bind('<Escape>', self.Cancel) #dismiss dialog, no save
        # self.bind('<Alt-a>', self.Apply) #apply changes, save
        # self.bind('<F1>', self.Help) #context help
        # Attach callbacks after loading config to avoid calling them.
        tracers.attach()

        self.grab_set()
        self.wm_deiconify()
        self.wait_window()

    def create_widgets(self):
        self.frame = Frame(self, padding="5px")

        # notebook
        self.note = Notebook(self.frame)
        self.note.add(FontPage(self.note), text='Fonts')
        self.note.add(HighPage(self.note), text='Colors')
        self.note.add(GenPage(self.note), text=' General ')
        self.note.enable_traversal()
        self.note.pack(side=TOP, expand=TRUE, fill=BOTH)
        
        # buttons
        buttons_frame = Frame(self.frame, padding=4)

        button_args = {
            'takefocus': FALSE,
            'padding': (6, 3)
        }

        Button(buttons_frame, text='Ok', command=self.ok, **button_args).pack(side=LEFT, padx=5)
        Button(buttons_frame, text='Apply', command=self.apply, **button_args).pack(side=LEFT, padx=5)
        Button(buttons_frame, text='Cancel', command=self.cancel, **button_args).pack(side=LEFT, padx=5)

        buttons_frame.pack(side=BOTTOM)

        self.frame.grid(sticky=NSEW)

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


class FontPage(Frame):

    def __init__(self, master):
        super().__init__(master)
        self.create_page_font_tab()
        self.load_font_cfg()
        self.load_tab_cfg()

    def create_page_font_tab(self):
        self.font_name = tracers.add(StringVar(self), self.var_changed_font)
        self.font_size = tracers.add(StringVar(self), self.var_changed_font)
        self.font_bold = tracers.add(BooleanVar(self), self.var_changed_font)
        self.space_num = tracers.add(IntVar(self), ('main', 'Indent', 'num-spaces'))

        # Define frames and widgets.
        frame_font = LabelFrame(self, borderwidth=2, relief=GROOVE, text=' Shell/Editor Font ')

        # frame_font.
        frame_font_name = Frame(frame_font)
        frame_font_param = Frame(frame_font)
        font_name_title = Label(frame_font_name, justify=LEFT, text='Font Face :')
        self.fontlist = Listbox(frame_font_name, height=15, takefocus=True, exportselection=FALSE)
        self.fontlist.bind('<ButtonRelease-1>', self.on_fontlist_select)
        self.fontlist.bind('<KeyRelease-Up>', self.on_fontlist_select)
        self.fontlist.bind('<KeyRelease-Down>', self.on_fontlist_select)
        scroll_font = Scrollbar(frame_font_name)
        scroll_font.config(command=self.fontlist.yview)
        self.fontlist.config(yscrollcommand=scroll_font.set)
        font_size_title = Label(frame_font_param, text='Size :')
        self.sizelist = DynOptionMenu(frame_font_param, self.font_size, None)
        self.bold_toggle = Checkbutton(frame_font_param, variable=self.font_bold, onvalue=1, offvalue=0, text='Bold')

        # Grid and pack widgets:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        frame_font.grid(row=0, column=0, padx=5, pady=5)

        # frame_font.
        frame_font_name.pack(side=TOP, padx=5, pady=5, fill=X)
        frame_font_param.pack(side=TOP, padx=5, pady=5, fill=X)
        font_name_title.pack(side=TOP, anchor=W)
        self.fontlist.pack(side=LEFT, expand=TRUE, fill=X)
        scroll_font.pack(side=LEFT, fill=Y)
        font_size_title.pack(side=LEFT, anchor=W)
        self.sizelist.pack(side=LEFT, anchor=W)
        self.bold_toggle.pack(side=LEFT, anchor=W, padx=20)

    def load_font_cfg(self):
        """Load current configuration settings for the font options.

        Retrieve current font with idleConf.GetFont and font families
        from tk. Setup fontlist and set font_name.  Setup sizelist,
        which sets font_size.  Set font_bold.  Call set_samples.
        """
        configured_font = idleConf.GetFont(self, 'main', 'EditorWindow')
        font_name = configured_font[0].lower()
        font_size = configured_font[1]
        font_bold  = configured_font[2]=='bold'

        # Set sorted no-duplicate editor font selection list and font_name.
        fonts = sorted(set(tkfont.families(self)))
        for font in fonts:
            self.fontlist.insert(END, font)
        self.font_name.set(font_name)
        lc_fonts = [s.lower() for s in fonts]
        try:
            current_font_index = lc_fonts.index(font_name)
            self.fontlist.see(current_font_index)
            self.fontlist.select_set(current_font_index)
            self.fontlist.select_anchor(current_font_index)
            self.fontlist.activate(current_font_index)
        except ValueError:
            pass
        # Set font size dropdown.
        self.sizelist.SetMenu(('7', '8', '9', '10', '11', '12', '13', '14',
                               '16', '18', '20', '22', '25', '29', '34', '40'),
                              font_size)
        # Set font weight.
        self.font_bold.set(font_bold)

    def var_changed_font(self, *params):
        """Store changes to font attributes.

        When one font attribute changes, save them all, as they are
        not independent from each other. In particular, when we are
        overriding the default font, we need to write out everything.
        """
        value = self.font_name.get()
        changes.add_option('main', 'EditorWindow', 'font', value)
        value = self.font_size.get()
        changes.add_option('main', 'EditorWindow', 'font-size', value)
        value = self.font_bold.get()
        changes.add_option('main', 'EditorWindow', 'font-bold', value)

    def on_fontlist_select(self, event):
        """Handle selecting a font from the list.

        Event can result from either mouse click or Up or Down key.
        Set font_name and example displays to selection.
        """
        item = ACTIVE if event.type.name == 'KeyRelease' else ANCHOR
        font = self.fontlist.get(item)
        self.font_name.set(font.lower())

    def load_tab_cfg(self):
        """Load current configuration settings for the tab options.

        Attributes updated:
            space_num: Set to value from idleConf.
        """
        # Set indent sizes.
        space_num = idleConf.GetOption(
            'main', 'Indent', 'num-spaces', default=4, type='int')
        self.space_num.set(space_num)

    def var_changed_space_num(self, *params):
        "Store change to indentation size."
        value = self.space_num.get()
        changes.add_option('main', 'Indent', 'num-spaces', value)


class HighPage(Frame):

    def __init__(self, master):
        super().__init__(master)
        self.cd = master.winfo_toplevel()
        self.style = Style(master)
        self.create_page_highlight()
        self.load_theme_cfg()

    def create_page_highlight(self):
        ...

    def load_theme_cfg(self):
        """Load current configuration settings for the theme options. """


class GenPage(Frame):

    def __init__(self, master):
        super().__init__(master)

        self.init_validators()
        self.create_page_general()
        self.load_general_cfg()

    def init_validators(self):
        digits_or_empty_re = re.compile(r'[0-9]*')
        def is_digits_or_empty(s):
            "Return 's is blank or contains only digits'"
            return digits_or_empty_re.fullmatch(s) is not None
        self.digits_only = (self.register(is_digits_or_empty), '%P',)

    def create_page_general(self):
        """Return frame of widgets for General tab.

        Enable users to provisionally change general options. Function
        load_general_cfg initializes tk variables and helplist using
        idleConf.  Radiobuttons startup_shell_on and startup_editor_on
        set var startup_edit. Radiobuttons save_ask_on and save_auto_on
        set var autosave. Entry boxes win_width_int and win_height_int
        set var win_width and win_height.  Setting var_name invokes the
        default callback that adds option to changes.

        Helplist: load_general_cfg loads list user_helplist with
        name, position pairs and copies names to listbox helplist.
        Clicking a name invokes help_source selected. Clicking
        button_helplist_name invokes helplist_item_name, which also
        changes user_helplist.  These functions all call
        set_add_delete_state. All but load call update_help_changes to
        rewrite changes['main']['HelpFiles'].

        Widgets for GenPage(Frame):  (*) widgets bound to self
            frame_window: LabelFrame
                frame_run: Frame
                    startup_title: Label
                    (*)startup_editor_on: Radiobutton - startup_edit
                    (*)startup_shell_on: Radiobutton - startup_edit
                frame_win_size: Frame
                    win_size_title: Label
                    win_width_title: Label
                    (*)win_width_int: Entry - win_width
                    win_height_title: Label
                    (*)win_height_int: Entry - win_height
                frame_cursor_blink: Frame
                    cursor_blink_title: Label
                    (*)cursor_blink_bool: Checkbutton - cursor_blink
                frame_autocomplete: Frame
                    auto_wait_title: Label
                    (*)auto_wait_int: Entry - autocomplete_wait
                frame_paren1: Frame
                    paren_style_title: Label
                    (*)paren_style_type: OptionMenu - paren_style
                frame_paren2: Frame
                    paren_time_title: Label
                    (*)paren_flash_time: Entry - flash_delay
                    (*)bell_on: Checkbutton - paren_bell
            frame_editor: LabelFrame
                frame_save: Frame
                    run_save_title: Label
                    (*)save_ask_on: Radiobutton - autosave
                    (*)save_auto_on: Radiobutton - autosave
                frame_format: Frame
                    format_width_title: Label
                    (*)format_width_int: Entry - format_width
                frame_line_numbers_default: Frame
                    line_numbers_default_title: Label
                    (*)line_numbers_default_bool: Checkbutton - line_numbers_default
                frame_context: Frame
                    context_title: Label
                    (*)context_int: Entry - context_lines
            frame_shell: LabelFrame
                frame_auto_squeeze_min_lines: Frame
                    auto_squeeze_min_lines_title: Label
                    (*)auto_squeeze_min_lines_int: Entry - auto_squeeze_min_lines
            frame_help: LabelFrame
                frame_helplist: Frame
                    frame_helplist_buttons: Frame
                        (*)button_helplist_edit
                        (*)button_helplist_add
                        (*)button_helplist_remove
                    (*)helplist: ListBox
                    scroll_helplist: Scrollbar
        """
        # Integer values need StringVar because int('') raises.
        self.startup_edit = tracers.add(IntVar(self), ('main', 'General', 'editor-on-startup'))
        self.win_width = tracers.add(StringVar(self), ('main', 'EditorWindow', 'width'))
        self.win_height = tracers.add(StringVar(self), ('main', 'EditorWindow', 'height'))
        self.cursor_blink = tracers.add(BooleanVar(self), ('main', 'EditorWindow', 'cursor-blink'))
        self.autocomplete_wait = tracers.add(StringVar(self), ('extensions', 'AutoComplete', 'popupwait'))
        self.paren_style = tracers.add(StringVar(self), ('extensions', 'ParenMatch', 'style'))
        self.flash_delay = tracers.add(StringVar(self), ('extensions', 'ParenMatch', 'flash-delay'))
        self.paren_bell = tracers.add(BooleanVar(self), ('extensions', 'ParenMatch', 'bell'))

        self.auto_squeeze_min_lines = tracers.add(StringVar(self), ('main', 'PyShell', 'auto-squeeze-min-lines'))

        self.autosave = tracers.add(IntVar(self), ('main', 'General', 'autosave'))
        self.format_width = tracers.add(StringVar(self), ('extensions', 'FormatParagraph', 'max-width'))
        self.line_numbers_default = tracers.add(BooleanVar(self), ('main', 'EditorWindow', 'line-numbers-default'))
        self.context_lines = tracers.add(StringVar(self), ('extensions', 'CodeContext', 'maxlines'))

        # Create widgets:
        # Section frames.
        frame_window = LabelFrame(self, borderwidth=2, relief=GROOVE, text=' Window Preferences')
        frame_editor = LabelFrame(self, borderwidth=2, relief=GROOVE, text=' Editor Preferences')

        # Frame_window.
        frame_run = Frame(frame_window, borderwidth=0)
        startup_title = Label(frame_run, text='At Startup')
        self.startup_editor_on = Radiobutton(frame_run, variable=self.startup_edit, value=1, text="Open Edit Window")
        self.startup_shell_on = Radiobutton(frame_run, variable=self.startup_edit, value=0, text='Open Shell Window')

        frame_win_size = Frame(frame_window, borderwidth=0)
        win_size_title = Label(frame_win_size, text='Initial Window Size  (in characters)')
        win_width_title = Label(frame_win_size, text='Width')
        self.win_width_int = Entry(frame_win_size, textvariable=self.win_width, width=3, validatecommand=self.digits_only, validate='key')
        win_height_title = Label(frame_win_size, text='Height')
        self.win_height_int = Entry(frame_win_size, textvariable=self.win_height, width=3, validatecommand=self.digits_only, validate='key')

        frame_cursor_blink = Frame(frame_window, borderwidth=0)
        cursor_blink_title = Label(frame_cursor_blink, text='Cursor Blink')
        self.cursor_blink_bool = Checkbutton(frame_cursor_blink, variable=self.cursor_blink, width=1)

        frame_autocomplete = Frame(frame_window, borderwidth=0,)
        auto_wait_title = Label(frame_autocomplete, text='Completions Popup Wait (milliseconds)')
        self.auto_wait_int = Entry(frame_autocomplete, width=6, textvariable=self.autocomplete_wait, validatecommand=self.digits_only, validate='key')

        frame_paren1 = Frame(frame_window, borderwidth=0)
        paren_style_title = Label(frame_paren1, text='Paren Match Style')
        self.paren_style_type = OptionMenu(frame_paren1, self.paren_style, 'expression', "opener","parens","expression")
        frame_paren2 = Frame(frame_window, borderwidth=0)
        paren_time_title = Label(frame_paren2, text='Time Match Displayed (milliseconds)\n' '(0 is until next input)')
        self.paren_flash_time = Entry(frame_paren2, textvariable=self.flash_delay, width=6)
        self.bell_on = Checkbutton(frame_paren2, text="Bell on Mismatch", variable=self.paren_bell)

        # Frame_editor.
        frame_save = Frame(frame_editor, borderwidth=0)
        run_save_title = Label(frame_save, text='At Start of Run (F5)  ')
        self.save_ask_on = Radiobutton(frame_save, variable=self.autosave, value=0, text="Prompt to Save")
        self.save_auto_on = Radiobutton(frame_save, variable=self.autosave, value=1, text='No Prompt')

        frame_format = Frame(frame_editor, borderwidth=0)
        format_width_title = Label(frame_format, text='Format Paragraph Max Width')
        self.format_width_int = Entry(frame_format, textvariable=self.format_width, width=4, validatecommand=self.digits_only, validate='key')

        frame_line_numbers_default = Frame(frame_editor, borderwidth=0)
        line_numbers_default_title = Label(frame_line_numbers_default, text='Show line numbers in new windows')
        self.line_numbers_default_bool = Checkbutton(frame_line_numbers_default, variable=self.line_numbers_default, width=1)

        frame_context = Frame(frame_editor, borderwidth=0)
        context_title = Label(frame_context, text='Max Context Lines :')
        self.context_int = Entry(frame_context, textvariable=self.context_lines, width=3, validatecommand=self.digits_only, validate='key')


        # Pack widgets:
        # Body.
        frame_window.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_editor.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        # frame_run.
        frame_run.pack(side=TOP, padx=5, pady=0, fill=X)
        startup_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.startup_shell_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        self.startup_editor_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        # frame_win_size.
        frame_win_size.pack(side=TOP, padx=5, pady=0, fill=X)
        win_size_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.win_height_int.pack(side=RIGHT, anchor=E, padx=10, pady=5)
        win_height_title.pack(side=RIGHT, anchor=E, pady=5)
        self.win_width_int.pack(side=RIGHT, anchor=E, padx=10, pady=5)
        win_width_title.pack(side=RIGHT, anchor=E, pady=5)
        # frame_cursor_blink.
        frame_cursor_blink.pack(side=TOP, padx=5, pady=0, fill=X)
        cursor_blink_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.cursor_blink_bool.pack(side=LEFT, padx=5, pady=5)
        # frame_autocomplete.
        frame_autocomplete.pack(side=TOP, padx=5, pady=0, fill=X)
        auto_wait_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.auto_wait_int.pack(side=TOP, padx=10, pady=5)
        # frame_paren.
        frame_paren1.pack(side=TOP, padx=5, pady=0, fill=X)
        paren_style_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.paren_style_type.pack(side=TOP, padx=10, pady=5)
        frame_paren2.pack(side=TOP, padx=5, pady=0, fill=X)
        paren_time_title.pack(side=LEFT, anchor=W, padx=5)
        self.bell_on.pack(side=RIGHT, anchor=E, padx=15, pady=5)
        self.paren_flash_time.pack(side=TOP, anchor=W, padx=15, pady=5)

        # frame_save.
        frame_save.pack(side=TOP, padx=5, pady=0, fill=X)
        run_save_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.save_auto_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        self.save_ask_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        # frame_format.
        frame_format.pack(side=TOP, padx=5, pady=0, fill=X)
        format_width_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.format_width_int.pack(side=TOP, padx=10, pady=5)
        # frame_line_numbers_default.
        frame_line_numbers_default.pack(side=TOP, padx=5, pady=0, fill=X)
        line_numbers_default_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.line_numbers_default_bool.pack(side=LEFT, padx=5, pady=5)
        # frame_context.
        frame_context.pack(side=TOP, padx=5, pady=0, fill=X)
        context_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.context_int.pack(side=TOP, padx=5, pady=5)


    def load_general_cfg(self):
        "Load current configuration settings for the general options."


class VarTrace:
    """Maintain Tk variables trace state."""

    def __init__(self):
        """Store Tk variables and callbacks.

        untraced: List of tuples (var, callback)
            that do not have the callback attached
            to the Tk var.
        traced: List of tuples (var, callback) where
            that callback has been attached to the var.
        """
        self.untraced = []
        self.traced = []

    def clear(self):
        "Clear lists (for tests)."
        # Call after all tests in a module to avoid memory leaks.
        self.untraced.clear()
        self.traced.clear()

    def add(self, var, callback):
        """Add (var, callback) tuple to untraced list.

        Args:
            var: Tk variable instance.
            callback: Either function name to be used as a callback
                or a tuple with IdleConf config-type, section, and
                option names used in the default callback.

        Return:
            Tk variable instance.
        """
        if isinstance(callback, tuple):
            callback = self.make_callback(var, callback)
        self.untraced.append((var, callback))
        return var

    @staticmethod
    def make_callback(var, config):
        "Return default callback function to add values to changes instance."
        def default_callback(*params):
            "Add config values to changes instance."
            changes.add_option(*config, var.get())
        return default_callback

    def attach(self):
        "Attach callback to all vars that are not traced."
        while self.untraced:
            var, callback = self.untraced.pop()
            var.trace_add('write', callback)
            self.traced.append((var, callback))

    def detach(self):
        "Remove callback from traced vars."
        while self.traced:
            var, callback = self.traced.pop()
            var.trace_remove('write', var.trace_info()[0][1])
            self.untraced.append((var, callback))


tracers = VarTrace()

import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    dialog = ConfigDialog(root)

    dialog.mainloop()
