import tkinter as tk

from tkinter import ttk, TclError

class AutoScrollbar(ttk.Scrollbar):
    """ Scrollbar that is only visible when needed. Only works with grid. """
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

    def set(self, first, last):
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)

class FadingLabel(ttk.Label):
    """ Label that fades back to an idle text after a given time """
    def __init__(self, master=None, delay=2500, **kw):
        """
        :param delay: delay after which the text return to idle
        """
        super().__init__(master=master, **kw)
        self._idle_text = self["text"]
        self._delay = delay

    def write(self, msg):
        self["text"] = msg
        self.after(self._delay, lambda: self.config(text=self._idle_text))


class ThemedText(tk.Text):
    """ Text widget that can be styled """
    def __init__(self, master=None, style="TText", **kw):

        super().__init__(master=master, **kw)

        self._apply_style(style)

    def _apply_style(self, widget_name):
        style = ttk.Style()

        style_config = style.configure('.')

        config = { k: style_config[k] for k in self.configure().keys() if k in style_config }
        config |= (style.configure(widget_name) or {})

        self.configure(config)

class ExtendedText(ThemedText):
    def __init__(self, master=None, **kw):
        """A text widget that report on internal widget commands"""
        super().__init__(master=master, **kw)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        try:
            result = self.tk.call((self._orig, command) + args)

            if command in ("insert", "delete", "replace"):
                self.event_generate("<<text-changed>>")
                self.event_generate("<<insert-moved>>")
            elif command in ("mark"):
                self.event_generate("<<insert-moved>>")
            
            return result
        except TclError as e:
            #print("ignore error:", command, *args)
            pass

    def set_tab_size(self, size):
        self['tabs'] = self.tk.call("font", "measure", self['font'], size * ' ')


######################################################################

######################################################################
import os

class ExtendendThemes():
    def __init__(self) -> None:
        self.style = ttk.Style()
        self.old_themes = self.style.theme_names()
        self.added_themes = []

    def load_from_files(self, *files):
        for file in files:
            self.style.tk.call('source', os.path.abspath(file))

        self.added_themes = [t for t in self.style.theme_names() if t not in self.old_themes]

    def load_from_str(self, *strings):
        for s in strings:
            self.style.tk.eval(s)
            
        self.added_themes = [t for t in self.style.theme_names() if t not in self.old_themes]

    #TODO: load from pkgIndex.tcl
    def load_from_index(self, dir, index_name='pkgIndex'):
        ...

    def theme_use(self, name):
        self.style.theme_use(name)