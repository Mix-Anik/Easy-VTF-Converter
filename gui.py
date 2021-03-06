from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.ttk import Progressbar
from vtf_converter import find_textures, convert
from explorers import getExplorerWindowPaths
from platform import system
from time import time


OS_TYPE = system()
version = "1.0"
supported_os = ["Windows"]


def clearConsole():
    console.configure(state=NORMAL)
    console.delete('1.0', END)
    console.configure(state=DISABLED)

def writeToConsole(text):
    console.configure(state=NORMAL)
    console.insert(INSERT, text+"\n")
    console.see(END)
    console.configure(state=DISABLED)

def convert_textures():
    progress["value"] = 0
    clearConsole()
    sel_path_idxs = path_selector.curselection()

    if len(sel_path_idxs) > 0:
        start_time = time()
        textures_paths = find_textures([path_selector.get(sel_path_idx) for sel_path_idx in sel_path_idxs])
        progress["value"] = 0

        writeToConsole("Found %s texture(s) in %s directory(ies)" % (len(textures_paths), len(sel_path_idxs)))
        writeToConsole("Converting to VTF version %s" % vervar.get())

        for i in range(len(textures_paths)):
            tex_path = textures_paths[i]
            convert(tex_path, vervar.get())
            progress["value"] += 100 / len(textures_paths)
            window.update()

        execution_time = round(time() - start_time, 2)
        writeToConsole("Done in %s seconds!" % execution_time)
    elif path_selector.size() == 0:
        writeToConsole("You don't have any directories open!")
    else:
        writeToConsole("You haven't selected any paths!")

def update_explorer_data(msg=True):
    clearConsole()
    path_selector.delete(0, END)
    explorer_paths = getExplorerWindowPaths()

    for path in explorer_paths:
        path_selector.insert(END, path)

    if msg: writeToConsole("Updated!")

if OS_TYPE in supported_os:
    # Main software window and frame setup
    window = Tk()
    window.geometry('500x275')
    window.resizable(False, False)
    window.title("Easy VTF Converter %s" % version)

    mainframe = Frame()
    mainframe.pack(padx=8, pady=8)
    mainframe.grid_rowconfigure(0, weight=1)
    mainframe.grid_columnconfigure(0, weight=1)

    # Left part of the window (the one with selection box)
    path_selector = Listbox(mainframe, selectmode="multiple", width=60)
    path_selector.grid(row=0, column=0, rowspan=5)
    path_selector.config(activestyle="none", background="#fefefe", fg="#000000", relief=SOLID)

    yscrollbar = Scrollbar(mainframe, orient="vertical")
    yscrollbar.config(command=path_selector.yview)
    yscrollbar.grid(row=0, column=1, rowspan=5, sticky=N+S)

    xscrollbar = Scrollbar(mainframe, orient="horizontal")
    xscrollbar.config(command=path_selector.xview)
    xscrollbar.grid(row=5, column=0, sticky=E+W)

    path_selector.config(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)

    # Right part of the window (buttons, selectors)
    versions = ['7.0', '7.1', '7.2', '7.3', '7.4', '7.5']
    vervar = StringVar(mainframe)
    vervar.set('7.2')

    # Version selector
    Label(mainframe, text="Convert to").grid(row=0, column=2)
    vselector = OptionMenu(mainframe, vervar, *versions)
    vselector.config(width=2, relief=SOLID, bd=1, fg="#000acc")
    vselector.grid(row=0, column=3, sticky=E+W)

    # Button's *onhover* handlers
    def ud_hover_in(e): update_btn['background'] = '#edfaff'
    def ud_hover_out(e): update_btn['background'] = 'SystemButtonFace'
    def cv_hover_in(e): convert_btn['background'] = '#edfaff'
    def cv_hover_out(e): convert_btn['background'] = 'SystemButtonFace'

    # Buttons
    update_btn = Button(mainframe, padx=6, text="Update", command=update_explorer_data)
    update_btn.config(relief=SOLID, bd=1, fg="#000acc")
    update_btn.grid(row=2, column=2, columnspan=2, pady=8, sticky=E+W)
    update_btn.bind("<Enter>", ud_hover_in)
    update_btn.bind("<Leave>", ud_hover_out)

    convert_btn = Button(mainframe, padx=6, text="Convert", command=convert_textures)
    convert_btn.config(relief=SOLID, bd=1, fg="#000acc", font=("TkDefaultFont", 10, "bold"))
    convert_btn.grid(row=3, column=2, columnspan=2, sticky=E+W)
    convert_btn.bind("<Enter>", cv_hover_in)
    convert_btn.bind("<Leave>", cv_hover_out)

    # Bottom part of the window (console and progress bar)
    console = Text(mainframe, relief=SUNKEN, background="gray85", foreground="#000000")
    console.config(height=6)
    console.grid(row=6, column=0, columnspan=4, pady=6, sticky=E+W)

    progress = Progressbar(mainframe, orient="horizontal", mode="determinate")
    progress.grid(row=7, column=0, columnspan=4, sticky=E+W)
    progress["maximum"] = 100
    progress["value"] = 0

    # adding choices to the selection box
    update_explorer_data(False)

    window.mainloop()

else:
    window = Tk()
    window.withdraw()
    showinfo("OS ERROR", "Unfortunately you are using unsupported type of OS." +
                         "\n\nCurrently supported are:\n- %s" % ("\n- ".join(supported_os)))