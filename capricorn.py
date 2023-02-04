import sys
from configparser import ConfigParser

# import tkinter
from tkinter import filedialog
import tkinter.messagebox as mbox

# import own stuff
from view import View
from workspace import Workspace

from dialog import AboutDialog, ConfigDialog

from lib.extendedTk import *

#============================================================================
# config
#============================================================================
DEFAULT_CONFIG = {
    'view': {
        'width': '1200',
        'height': '800',
        'state': 'normal'
    },
    'workspace': {
        'font': '"Courier New" 10',
        'text_width': '128',
        'last_file': ''
    },
    'colors': {
        'fg_main':      '#e1e4e8',
        'bg_main':      '#454545',
        'bg_status':    '#2f2f2f',
        'fg_text':      '#000000',
        'bg_text':      '#f1f1f1',
        'scrollbar':    '#6f6f6f',
    },
    'tag.title': {
        'foreground': '#a968c2',
        'font':
        '"Courier New" 24 bold'
    },
    'tag.separator': {
        'foreground': '#6f6f6f',
        'font': '"Courier New" 16',
        'justify': 'center',
        'spacing1': '12',
        'spacing3': '12'
    }
}

def get_tags(config, prefix='tag.'):
    tags = {}
    for name in config.sections():
        if name.startswith(prefix):
            tags[name.removeprefix(prefix)] = dict(config[name])
    return tags

FILEDIALOG_OPTIONS = {
    "defaultextension" : ".txt",
    "filetypes": [ ("All Files", "*.*") ]
}

#============================================================================
# capricorn / controller
#============================================================================
class Capricorn():
    def __init__(self, config_path, filename):

        # create view and workspace
        self.view = View()
        self.workspace = Workspace(self.view)

        # parse config file
        config = ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        config.read(config_path)

        self.config_path = config_path
        # apply config
        self.config = {}
        self.load_config({
            'view':      dict(config['view']),
            'workspace': dict(config['workspace']),
            'colors':    dict(config['colors']),
            'patterns':  dict(config['patterns']),
            'tags':      get_tags(config),
        })

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
        path = filename or self.config['workspace']['last_file']
        if path:
            self.workspace.read_file(path)

        self.update_title()

    def load_config(self, config):
        self.config |= config

        self.view.load_config(self.config['view'])
        self.view.load_theme(self.config['colors'])
        self.view.load_tags(self.config['tags'])
        self.workspace.load_config(self.config['workspace'])

    def save_config(self):
        # update view config
        if not self.view.zoomed():
            self.config['view']['width'] = self.view.winfo_width()
            self.config['view']['height'] = self.view.winfo_height()

        self.config['view']['state'] = 'zoomed' if self.view.zoomed() else 'normal'

        # update workspace config
        self.config['workspace']['last_file'] = self.workspace.path or ''

        # tags
        for name, settings in self.config.pop('tags').items():
            self.config[f'tag.{name}'] = settings

        # write to config file
        config = ConfigParser()
        config.read_dict(self.config)

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

    def run(self):
        self.view.mainloop()

    def on_text_change(self, event):
        self.workspace.update_word_count()

        # tag all patterns
        for tag, pattern in self.config['patterns'].items():
            self.workspace.tag_pattern(pattern, tag)

        if self.workspace.set_unsaved():
            self.update_title()

    def on_insert_move(self, event):
        self.workspace.update_insert_pos()

    def show_about(self, event):
        AboutDialog(event.widget)
        return 'break'

    def show_settings(self, event):
        ConfigDialog(event.widget, None, self.config, self.load_config)
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

    def exit(self, *args):
        # save config
        self.save_config()

        # aks to save and close
        if self.check_saved():
            self.view.destroy()

#TODO: color picker entry
#TODO: tags dialog
#TODO: latex exporter
if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else None

    app = Capricorn("config.ini", filename)
    app.run()

