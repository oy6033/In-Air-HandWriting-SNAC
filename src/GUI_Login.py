import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import GUI_Main


class App:
    def __init__(self, master):
        self.master = master
        self.create()

    def create(self):
        self.master.geometry("600x400")
        self.fm = Frame(self.master)
        ttk.Button(self.fm, text='Leap Motion', command=self.leap, width=200).pack(side=TOP, fill=BOTH, expand=1)
        ttk.Button(self.fm, text='Glove', command=self.leap, width=200).pack(side=TOP, fill=BOTH, expand=1)
        ttk.Button(self.fm, text='Bottom', command=self.leap, width=200).pack(side=TOP, fill=BOTH, expand=1)
        self.fm.pack(fill=BOTH, expand=YES)

    def leap(self):
        self.fm.quit()
        self.fm.destroy()
        GUI_Main.Application(self.master)


if __name__ == '__main__':
    root = Tk()
    root.title("In-Air Hand Writing")
    display = App(root)
    root.mainloop()

#
# if __name__ == '__main__':
#
#     app = GUI_Main.Application()
#     app.protocol("WM_DELETE_WINDOW", app._quit)
#     app.mainloop()

# root = Tk()
# root.title('111')
# LoginPage(root)
# root.mainloop()