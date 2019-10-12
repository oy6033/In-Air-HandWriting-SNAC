import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import GUI_Main
import sys


class Application(object):
    def __init__(self, master=None, input=None):
        self.master = master
        self.input = input
        self.master.protocol("WM_DELETE_WINDOW", self._quit)
        self.create()

    def create(self,w=600, h=400):
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.fm = Frame(self.master)
        ttk.Button(self.fm, text='Leap Motion', command=self.leap, width=200).pack(side=TOP, fill=BOTH, expand=1)
        ttk.Button(self.fm, text='Glove', command=self.leap2, width=200).pack(side=TOP, fill=BOTH, expand=1)
        ttk.Button(self.fm, text='Bottom', width=200).pack(side=TOP, fill=BOTH, expand=1)
        self.fm.pack(fill=BOTH, expand=YES)

    def leap(self):
        # self.fm.quit()
        self.fm.destroy()
        GUI_Main.Application(self.master, "1", self.input)

    def leap2(self):
        # self.fm.quit()
        self.fm.destroy()
        GUI_Main.Application(self.master, "2", self.input)


    def _quit(self):
        print ("application is closed")
        self.master.quit()
        self.master.destroy()
        sys.exit()


if __name__ == '__main__':
    input = None
    try:
        input = sys.argv[1]
    except:
        input = '/dev/ttyACM0'
        print "No parameter detect"
    root = Tk()
    root.title("In-Air Hand Writing")
    display = Application(root, input)
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