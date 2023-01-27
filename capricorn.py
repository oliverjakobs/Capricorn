import sys
from configparser import ConfigParser

# import tkinter
from tkinter import filedialog
import tkinter.messagebox as mbox

# import own stuff
from view import View
from workspace import Workspace

from dialog import AboutDialog

from lib.extendedTk import *

#============================================================================
# capricorn / controller
#============================================================================
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
        'fg_title':  '#a968c2',
        'scrollbar': '#6f6f6f'
    },
    'fonts': {
        'main': '"Courier New" 10',
        'title': '"Courier New" 24 bold',
        'separator': '"Courier New" 16'
    }
}

FILEDIALOG_OPTIONS = {
    "defaultextension" : ".txt",
    "filetypes": [ ("All Files", "*.*") ]
}

class Capricorn():
    def __init__(self, config_path, filename):

        # parse config file
        config = ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        config.read(config_path)

        self.view_config = dict(config['view'])
        self.ws_config = dict(config['workspace'])
        self.colors = dict(config['colors'])
        self.fonts = dict(config['fonts'])

        self.config_path = config_path

        #view
        self.view = View(self.view_config, self.colors, self.fonts)

        # workspace
        self.workspace = Workspace(self.ws_config, self.view)

        # bind events
        self.view.bind("<<text-changed>>", self.on_text_change)
        self.view.bind("<<insert-moved>>", self.on_insert_move)

        self.view.bind('<<new>>', self.new_file)
        self.view.bind('<<open>>', self.open)
        self.view.bind('<<save>>', self.save)
        self.view.bind('<<save-as>>', self.save_as)
        self.view.bind('<<wnd-close>>', self.exit)

        self.view.bind('<<show-about>>', self.show_about)
        self.view.bind('<<show-settings>>', self.show_settings)

        self.view.protocol("WM_DELETE_WINDOW", self.exit)

        # read file
        path = filename or self.ws_config['last_file']
        if path:
            self.workspace.read_file(path)

        self.update_title()

    def run(self):
        self.view.mainloop()

    def on_text_change(self, event):
        self.workspace.update_word_count()
        self.workspace.tag_pattern(r"#[^\n]*", "title")
        self.workspace.tag_pattern(r"\*\*\*", "separator")

        if self.workspace.set_unsaved():
            self.update_title()

    def on_insert_move(self, event):
        self.workspace.update_insert_pos()

    def show_about(self, event):
        AboutDialog(event.widget)
        return 'break'

    def show_settings(self, event):
        print("Settings")
        return 'break'

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
        result = mbox.askyesnocancel(title=title, message=prompt, default=mbox.YES)

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

    def save_config(self):
        config = ConfigParser()
        config['view'] = self.view.get_config(self.view_config)
        config['workspace'] = self.workspace.get_config(self.ws_config)
        config['colors'] = self.colors
        config['fonts'] = self.fonts

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)


    def exit(self, *args):
        # save config
        self.save_config()

        # save and close
        if self.check_saved():
            self.view.destroy()

#TODO: style, font selector popup
#TODO: latex exporter
#TODO: fonts/colors tcl-array loading
if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = Capricorn("config.ini", filename)
    app.run()

