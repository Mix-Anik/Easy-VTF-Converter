import tkinter as tk

from tkinter.messagebox import showinfo
from tkinter.ttk import Progressbar
from platform import system
from time import time

from src.helpers import find_textures
from src.explorers import get_explorer_window_paths
from src.vtf_structs import VTFFile


OS_TYPE = system()
VERSION = "1.1"
supported_os = ["Windows"]


def clear_console():
    console.configure(state=tk.NORMAL)
    console.delete('1.0', tk.END)
    console.configure(state=tk.DISABLED)


def write_to_console(text):
    console.configure(state=tk.NORMAL)
    console.insert(tk.INSERT, text+"\n")
    console.see(tk.END)
    console.configure(state=tk.DISABLED)


def convert_single_texture(texture_path, version):
    tex_file = open(texture_path, mode="r+b")
    bytelist = tex_file.read()
    tex_file.close()

    minor_version = int(version[-1])

    # Just in case, so it wouldn't stop processing other files
    try:
        # Creating VTF-type object & converting to requested version
        vtf = VTFFile(bytelist)
        vtf.convert(minor_version)

        # Writing new file (replacing old one)
        tex_file = open(texture_path, 'wb')
        tex_file.write(vtf.compose())
        tex_file.close()
    except Exception:
        write_to_console(f'Failed to convert "{texture_path}"')


def convert_textures():
    progress["value"] = 0
    clear_console()
    sel_path_idxs = path_selector.curselection()

    if len(sel_path_idxs) > 0:
        start_time = time()
        textures_paths = find_textures([path_selector.get(sel_path_idx) for sel_path_idx in sel_path_idxs])
        progress["value"] = 0

        write_to_console("Found %s texture(s) in %s directory(ies)" % (len(textures_paths), len(sel_path_idxs)))
        write_to_console("Converting to VTF version %s" % vervar.get())

        for i in range(len(textures_paths)):
            tex_path = textures_paths[i]
            convert_single_texture(tex_path, vervar.get())
            progress["value"] += 100 / len(textures_paths)
            window.update()

        execution_time = round(time() - start_time, 2)
        write_to_console("Done in %s seconds!" % execution_time)
    elif path_selector.size() == 0:
        write_to_console("You don't have any directories open!")
    else:
        write_to_console("You haven't selected any paths!")


def update_explorer_data(msg=True):
    clear_console()
    path_selector.delete(0, tk.END)
    explorer_paths = get_explorer_window_paths()

    for path in explorer_paths:
        path_selector.insert(tk.END, path)

    if msg:
        write_to_console("Updated!")


if OS_TYPE in supported_os:
    # Main software window and frame setup
    window = tk.Tk()
    window.geometry('500x275')
    window.resizable(False, False)
    window.title("Easy VTF Converter %s" % VERSION)

    mainframe = tk.Frame()
    mainframe.pack(padx=8, pady=8)
    mainframe.grid_rowconfigure(0, weight=1)
    mainframe.grid_columnconfigure(0, weight=1)

    # Left part of the window (the one with selection box)
    path_selector = tk.Listbox(mainframe, selectmode="multiple", width=60)
    path_selector.grid(row=0, column=0, rowspan=5)
    path_selector.config(activestyle="none", background="#fefefe", fg="#000000", relief=tk.SOLID)

    yscrollbar = tk.Scrollbar(mainframe, orient="vertical")
    yscrollbar.config(command=path_selector.yview)
    yscrollbar.grid(row=0, column=1, rowspan=5, sticky=tk.N + tk.S)

    xscrollbar = tk.Scrollbar(mainframe, orient="horizontal")
    xscrollbar.config(command=path_selector.xview)
    xscrollbar.grid(row=5, column=0, sticky=tk.E + tk.W)

    path_selector.config(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)

    # Right part of the window (buttons, selectors)
    versions = ['7.0', '7.1', '7.2', '7.3', '7.4', '7.5']
    vervar = tk.StringVar(mainframe)
    vervar.set('7.2')

    # Version selector
    tk.Label(mainframe, text="Convert to").grid(row=0, column=2)
    vselector = tk.OptionMenu(mainframe, vervar, *versions)
    vselector.config(width=2, relief=tk.SOLID, bd=1, fg="#000acc")
    vselector.grid(row=0, column=3, sticky=tk.E + tk.W)

    # Button's *onhover* handlers
    def ud_hover_in(e): update_btn['background'] = '#edfaff'
    def ud_hover_out(e): update_btn['background'] = 'SystemButtonFace'
    def cv_hover_in(e): convert_btn['background'] = '#edfaff'
    def cv_hover_out(e): convert_btn['background'] = 'SystemButtonFace'

    # Buttons
    update_btn = tk.Button(mainframe, padx=6, text="Update", command=update_explorer_data)
    update_btn.config(relief=tk.SOLID, bd=1, fg="#000acc")
    update_btn.grid(row=2, column=2, columnspan=2, pady=8, sticky=tk.E + tk.W)
    update_btn.bind("<Enter>", ud_hover_in)
    update_btn.bind("<Leave>", ud_hover_out)

    convert_btn = tk.Button(mainframe, padx=6, text="Convert", command=convert_textures)
    convert_btn.config(relief=tk.SOLID, bd=1, fg="#000acc", font=("TkDefaultFont", 10, "bold"))
    convert_btn.grid(row=3, column=2, columnspan=2, sticky=tk.E + tk.W)
    convert_btn.bind("<Enter>", cv_hover_in)
    convert_btn.bind("<Leave>", cv_hover_out)

    # Bottom part of the window (console and progress bar)
    console = tk.Text(mainframe, relief=tk.SUNKEN, background="gray85", foreground="#000000")
    console.config(height=6)
    console.grid(row=6, column=0, columnspan=4, pady=6, sticky=tk.E + tk.W)

    progress = Progressbar(mainframe, orient="horizontal", mode="determinate")
    progress.grid(row=7, column=0, columnspan=4, sticky=tk.E + tk.W)
    progress["maximum"] = 100
    progress["value"] = 0

    # adding choices to the selection box
    update_explorer_data(False)
    window.mainloop()
else:
    window = tk.Tk()
    window.withdraw()
    showinfo("OS ERROR", "Unfortunately you are using unsupported type of OS." +
                         "\n\nCurrently supported are:\n- %s" % ("\n- ".join(supported_os)))
