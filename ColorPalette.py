import traceback
from tkinter import *
from tkinter import scrolledtext, messagebox
import threading
import win32api
import time
import json
from tkinter.filedialog import *


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


def get_color_on_mouse_click(label):
    state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
    while True:
        a = win32api.GetKeyState(0x01)
        if a != state_left:  # Button state changed
            state_left = a
            print(a)
            if a < 0:
                print('Left Button Pressed')
                x, y = win32api.GetCursorPos()
                print(win32api.GetCursorPos())
                import PIL.ImageGrab

                im = PIL.ImageGrab.grab()
                r, g, b = im.getpixel((x, y))
                label.config(bg=_from_rgb((r, g, b)))
                return im.getpixel((x, y))

        time.sleep(0.001)


def prep(event):
    thread = threading.Thread(target=get_color_on_mouse_click, args=(event.widget,))
    print(event.widget.cget('bg'))
    thread.start()

    event.widget.focus_set()  # give keyboard focus to the label
    event.widget.bind('<Key>', edit)


def edit(event):
    print(event.char)


def show_message(message: str, title=None):
    if title is None:
        messagebox.showinfo(title=message, message=message)
    else:
        messagebox.showinfo(title=title, message=message)


def draw_new_color_label(frame, color_rgb='#ffffff'):
    color_label = Label(frame, bg=color_rgb, width=5, height=2, borderwidth=2, relief="groove")
    color_label.bind('<Button-1>', prep)
    color_label.pack(side=LEFT, padx=5, pady=5)
    return color_label


color_lines = []

color_line_comments = []
color_lines_frames = []


def draw_new_color_line(color_label_count=8, color_line_comment_old_data=None, color_label_old_data=None):
    frame = Frame(window)
    global color_line_comments
    color_line_comment = Entry(frame, font=("Arial Bold", 13), width=20)
    color_line_comment.pack(side=LEFT, padx=5, pady=5)

    if color_line_comment_old_data:
        color_line_comment.insert(INSERT, color_line_comment_old_data)

    color_line_comments.append(color_line_comment)

    color_line = []
    global color_lines
    color_lines.append(color_line)

    if color_label_old_data:
        for n in color_label_old_data:
            color_label = draw_new_color_label(frame, color_rgb=n)
            color_line.append(color_label)
    else:
        for n in range(color_label_count):
            color_label = draw_new_color_label(frame, color_rgb='#ffffff')
            color_line.append(color_label)

    frame.pack(anchor=W, padx=10, pady=1)
    global color_lines_frames
    color_lines_frames.append(frame)


def draw_header():
    f_top = Frame(window)

    lbl = Label(f_top, text="Palette description", font=("Arial Bold", 10))
    lbl.pack(anchor=W)
    global comment_filed
    comment_filed = scrolledtext.ScrolledText(f_top, width=80, height=4)
    comment_filed.pack(expand=True)

    f_top.pack(anchor=W, padx=10, pady=10)

    f_add_btn = Frame(window)
    btn = Button(f_add_btn, text="+", font=("Arial Bold", 10), command=draw_new_color_line).pack()
    f_add_btn.pack(anchor=W, padx=10, pady=2)


def clear_data():
    global color_lines
    for color_line in color_lines:
        for n in color_line:
            n.destroy()
    color_lines = []

    global color_line_comments
    for n in color_line_comments:
        n.destroy()
    comment_filed.delete('1.0', END)
    color_line_comments = []

    global color_lines_frames
    for color_lines_frame in color_lines_frames:
        color_lines_frame.destroy()
    color_lines_frames = []


def open_file():
    rep = askopenfilenames(
        # parent=root,
        initialdir='/',
        initialfile='',
        filetypes=[
            ("JSON", "*.json"),
            ("All files", "*")])
    try:
        return rep[0]
    except IndexError:
        print("No file selected")


def load_data():
    file_name = open_file()
    print(file_name)

    try:
        with open(file_name, 'r') as f:
            data = json.load(f)

            if data.get("color_lines"):
                clear_data()

                if data.get("comment"):
                    comment_filed.insert(INSERT, data["comment"])

                for color_line in data["color_lines"]:
                    draw_new_color_line(color_line_comment_old_data=color_line["comment"],
                                        color_label_old_data=color_line["color_line_data"])
            else:
                show_message("Invalid file format ")
    except Exception as ex:
        show_message(message=traceback.format_exc(), title="Error loading file ")


def file_save(text):
    f = asksaveasfile(mode='w', defaultextension=".json")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f.write(text)
    f.close()  #


def save_data():
    data = {}
    data.update({"comment": comment_filed.get('1.0', 'end')})
    data.update({"color_lines": []})

    for i, color_line in enumerate(color_lines):
        color_line_data = {}
        color_line_data.update({"comment": color_line_comments[i].get()})
        color_line_data.update({"color_line_data": [x.cget('bg') for x in color_line]})
        data["color_lines"].append(color_line_data)

    file_save(json.dumps(data, ensure_ascii=False))


def _onKeyRelease(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")


if __name__ == '__main__':
    window = Tk()
    window.geometry('640x800')
    window.attributes("-topmost", True)
    window.bind_all("<Key>", _onKeyRelease, "+")
    window.title("Color palette")

    menu = Menu(window)
    new_item = Menu(menu, tearoff=0)
    new_item.add_command(label='New', command=clear_data)
    new_item.add_command(label='Open', command=load_data)
    new_item.add_command(label='Save', command=save_data)
    menu.add_cascade(label='File', menu=new_item)

    window.config(menu=menu)

    draw_header()

    window.mainloop()
