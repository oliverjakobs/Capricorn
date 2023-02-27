
import re, os

import tkinter as tk
import tkinter.messagebox as mbox

from view import View

#============================================================================
# workspace / model
#============================================================================
class Workspace():
    def __init__(self, view: View) -> None:
        self.text = view.text

        self.word_count = tk.StringVar(value="Wordcount: -")
        self.insert_pos = tk.StringVar(value="Ln -, Col -")
        
        view.label_word_count['textvariable'] = self.word_count
        view.label_insert_pos['textvariable'] = self.insert_pos

        self.saved = True
        self.set_filename(None)

    def load_config(self, config: dict) -> None:
        self.text.configure({
            'width': config['text_width'],
            'font': config['font']
        })

    def set_filename(self, filename: str) -> None:
        self.path = os.path.abspath(filename) if filename else None
        self.filename = os.path.basename(filename) if filename else "untitled"

    def get_title(self) -> str:
        return self.filename if self.saved else '*' + self.filename

    def tag_pattern(self, pattern: str, tag: str) -> None:
        # remove tag
        self.text.tag_remove(tag, "1.0", tk.END)

        # find and highlight all matches
        lines = self.text.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            for match in re.finditer(pattern, line):
                index1 = f"{i + 1}.{match.start()}"
                index2 = f"{i + 1}.{match.end()}"
                self.text.tag_add(tag, index1, index2)

    def update_insert_pos(self) -> None:
        ln, col = self.text.index('insert').split('.')
        self.insert_pos.set(f"Ln {ln}, Col {col}")

    def update_word_count(self) -> None:
        count = len(re.findall('\w+', self.text.get('1.0', 'end-1c')))
        self.word_count.set(f"Wordcount: {count}")

    def new_file(self) -> None:
        self.text.delete('1.0', tk.END)
        # prevent undoing clearing the text
        self.text.edit_reset()

        self.saved = True
        self.set_filename(None)

    def read_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r') as f:
                text = f.read()
                # clear text
                self.text.delete('1.0', tk.END)
                # insert new text
                self.text.insert('1.0', text)
                # prevent undoing reading the file
                self.text.edit_reset()
        except Exception as e:
            mbox.showerror(type(e).__name__, f"Could not open {filename}:\n{e}")
            return False

        self.saved = True
        self.set_filename(filename)
        return True

    def write_file(self, filename: str) -> bool:
        try:
            with open(filename, 'w') as f:
                f.write(self.text.get('1.0', 'end-1c'))
        except Exception as e:
            mbox.showerror("Error", f"Could not save {filename}:\n{e}")
            return False

        self.saved = True
        self.set_filename(filename)
        return True