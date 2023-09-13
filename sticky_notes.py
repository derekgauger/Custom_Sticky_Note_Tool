import tkinter as tk
from tkinter import Text, Scrollbar
import re
from tkinter import font as tkFont
import pickle
import sys, os

def get_exe_location():
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller runtime, return the path to the .exe file
        return sys.executable
    else:
        # Regular Python runtime, return the current script's directory
        return os.path.abspath(os.path.dirname(__file__))

def save_data():
    directory = os.path.dirname(get_exe_location())
    with open(os.path.join(directory, "sticky_note.pkl"), "wb") as f:
        # Get all the text from the Text widget
        note_data = text_widget.get("1.0", "end-1c")
        pickle.dump(note_data, f)

def delete_line(event):
    text_widget = event.widget
    cursor_index = text_widget.index(tk.INSERT)
    line_number, _ = map(int, cursor_index.split('.'))
    line_start = f"{line_number}.0"
    line_end = f"{line_number}.end + 1 char"  # +1 char to delete the newline at the end of the line
    text_widget.delete(line_start, line_end)

def apply_markdown(text_widget):
    text_widget.tag_remove("bullet", "1.0", "end")
    content = text_widget.get("1.0", "end").strip()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        apply_bullet(text_widget, i + 1, line)
    save_data()


def apply_bullet(text_widget, line_number, line_content):
    bullet_pattern = r"^-"
    if re.match(bullet_pattern, line_content.lstrip()):
        text_widget.tag_add("bullet", f"{line_number}.0", f"{line_number}.end")

def handle_return(event):
    text_widget = event.widget
    cursor_index = text_widget.index(tk.INSERT)
    line_number, col_number = map(int, cursor_index.split('.'))
    line_start = f"{line_number}.0"
    line_end = f"{line_number}.end"
    line_content = text_widget.get(line_start, line_end)

    num_tabs = len(line_content) - len(line_content.lstrip('\t'))

    if line_content.lstrip().startswith("- "):
        if line_content.lstrip() == "- ":
            text_widget.delete(line_start, line_end)
        else:
            text_widget.insert(tk.INSERT, "\n{}- ".format('\t' * num_tabs))
        save_data()
        return "break"
    save_data()
    

def handle_tab(event):
    text_widget = event.widget
    cursor_index = text_widget.index(tk.INSERT)
    line_number, col_number = map(int, cursor_index.split('.'))
    line_start = f"{line_number}.0"
    line_end = f"{line_number}.end"
    line_content = text_widget.get(line_start, line_end)

    if line_content.lstrip().startswith("- "):
        text_widget.insert(line_start, "\t")
        save_data()
        return "break"
    save_data()

def ctrl_backspace(event):
    text_widget = event.widget
    all_text = text_widget.get("1.0", "insert")
    end = len(all_text)
    start = end - 1
    while start > 0 and not all_text[start].isspace():
        start -= 1
    start_index = "1.0 + %d chars" % start
    end_index = "1.0 + %d chars" % end
    text_widget.delete(start_index, end_index)
    return "break"


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sticky Note")

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    custom_font = tkFont.Font(family="Helvetica", size=14)
    text_widget = Text(root, wrap=tk.WORD, yscrollcommand=scrollbar.set, undo=True, font=custom_font)
    text_widget.pack(expand=1, fill=tk.BOTH)

    scrollbar.config(command=text_widget.yview)

    text_widget.tag_configure("bullet", lmargin1=20, lmargin2=20)
    text_widget.config(bg="#363636", fg="white", insertbackground="white")

    text_widget.bind("<KeyRelease>", lambda event: apply_markdown(text_widget))
    text_widget.bind("<Return>", handle_return)
    text_widget.bind("<Tab>", handle_tab)
    text_widget.bind('<Control-x>', delete_line)
    text_widget.bind('<Control-BackSpace>', ctrl_backspace)

    try:
        directory = os.path.dirname(get_exe_location())
        with open(os.path.join(directory, "sticky_note.pkl"), "rb") as f:
            note_data = pickle.load(f)
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", note_data)
        apply_markdown(text_widget)
    except FileNotFoundError:
        pass

    root.mainloop()
