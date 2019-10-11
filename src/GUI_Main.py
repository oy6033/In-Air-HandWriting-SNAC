import datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from PIL import ImageTk
import PIL.Image
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os, sys, inspect, subprocess
if not os.path.exists('../data'):
    os.makedirs('../data')
if not os.path.exists('../video'):
    os.makedirs('../video')
import GUI_LeapMotion
import GUI_Camera





class Application(object):

    def __init__(self, master =None):
        self.master = master
        self.maxtimes = 5
        self.master.geometry("1180x800")
        self.master.title("In-Air Hand Writing")
        self.l = None
        self.createWidgets()

    def createWidgets(self):
        mianFram = Frame(master=self.master)
        mianFram.pack(fill='both', expand=YES)
        mianFram.bind_all('<Escape>', self.stop_camera)
        mianFram.bind_all('<Return>', self.push_enter)

        self.fig = plt.figure(figsize=(5, 6))
        self.ax1 = self.fig.add_subplot(2, 1, 1, projection='3d')

        self.ax2 = self.fig.add_subplot(2, 1, 2, projection='3d')

        self.canvas = FigureCanvasTkAgg(self.fig, master=mianFram)
        toolbarFrame = tk.Frame(master=mianFram)
        toolbarFrame.pack(fill='both', side=BOTTOM)
        self.canvas._tkcanvas.pack(fill='both', side=LEFT)
        self.ax1.mouse_init()
        self.ax2.mouse_init()
        toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        toolbar.update()

        inputFrame = tk.Frame(master=mianFram)
        inputFrame.pack(fill='both', side=LEFT, expand=YES)
        imageFrame = tk.Frame(master=inputFrame)

        self.canvasImage = Canvas(master=imageFrame, width=40)
        self.canvasImage.pack(fill='both', side=LEFT, expand=YES)
        self.my_images = []
        self.image_options = []
        for i in range(1, 125):
            self.image_options.append(str(i))
            temp = str(i) + '.png'
            img = PIL.Image.open('../img/p1dl1r3qbjceq3e41qfv114e1ufk4-' + temp)
            img = img.resize((300, 388), PIL.Image.ANTIALIAS)
            self.my_images.append(ImageTk.PhotoImage(img))
        self.images_index = 0
        self.image_on_canvas = self.canvasImage.create_image(150, 150, image=self.my_images[self.images_index])

        self.image_v = StringVar()
        self.image_v.set("1")

        comboboxFrame = tk.Frame(master=imageFrame)
        w = ttk.Combobox(master=comboboxFrame, textvariable=self.image_v, values=self.image_options, justify='center',
                         width=37)
        w.pack(fill=X, side=LEFT)
        w.bind("<<ComboboxSelected>>", self.choose_image)
        w.bind("<space>", self.choose_image)
        comboboxFrame.pack(fill='both', expand=YES)

        nextButtonFrame = tk.Frame(master=imageFrame)
        ttk.Button(master=nextButtonFrame, text='Prev', command=self.prev_image).pack(fill=X, side=LEFT, expand=YES)
        ttk.Button(master=nextButtonFrame, text='Next', command=self.next_image).pack(fill=X, side=LEFT, expand=YES)
        nextButtonFrame.pack(fill='both', expand=YES)
        imageFrame.pack(fill='both', expand=YES)

        cameraFrame = tk.Frame(master=imageFrame)
        ttk.Button(master=cameraFrame, text='Open Camera', command=self.camera_thread).pack(fill=X, side=LEFT,
                                                                                            expand=YES)
        cameraFrame.pack(fill='both', expand=YES)

        accountFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=accountFrame, text="Please input your account:", width=40).pack(fill=X, side=LEFT)
        self.account = ttk.Entry(master=accountFrame, width=40)
        self.account.bind('<Control-KeyRelease-a>', self.select_all)
        self.account.pack(fill=X, side=RIGHT)
        accountFrame.pack(fill='both', expand=YES)

        writingFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=writingFrame, text="Please input your writing word:", width=40).pack(fill=X, side=LEFT)
        self.password = ttk.Entry(master=writingFrame, width=40)
        self.password.bind('<Control-KeyRelease-a>', self.select_all)
        self.password.pack(fill=X, side=RIGHT)
        writingFrame.pack(fill='both', expand=YES)

        suffixFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=suffixFrame, text="Please input suffix if needed:", width=40).pack(fill=X, side=LEFT)
        self.suffix = ttk.Entry(master=suffixFrame, width=40)
        self.suffix.bind('<Control-KeyRelease-a>', self.select_all)
        self.suffix.pack(fill=X, side=RIGHT)
        suffixFrame.pack(fill='both', expand=YES)

        dropListFrame = tk.Frame(master=inputFrame)
        dropListFrame.bind('<Return>', self.push_enter)
        self.OPTIONS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.initialTimes = 0
        self.variable = StringVar(master=dropListFrame)
        self.variable.set(self.OPTIONS[self.initialTimes])
        ttk.Label(master=dropListFrame, text="Writing Times:", width=40).pack(fill=X, side=LEFT)
        dropList = OptionMenu(dropListFrame, self.variable, *self.OPTIONS)
        dropList.pack(fill=X, side=RIGHT)
        MODES = [
            ("5 times", 5),
            ("10 times", 10),
        ]
        self.v = IntVar()
        self.v.set(5)
        for text, mode in MODES:
            b = ttk.Radiobutton(dropListFrame, text=text,
                                variable=self.v, value=mode, command=self.updateOption)
            b.pack(fill=X, side=LEFT, expand=YES)
        dropListFrame.pack(fill='both', expand=YES)

        #buttonFrame
        buttonFrame = tk.Frame(master=inputFrame)
        ttk.Button(master=buttonFrame, text='Draw', command=self.thread).pack(fill=X, side=LEFT, expand=YES)
        ttk.Button(master=buttonFrame, text='Kill All', command=self.kill_all).pack(fill=X, side=LEFT, expand=YES)
        buttonFrame.pack(fill='both', expand=YES)

        noteBookFrame = tk.Frame(master=inputFrame)
        self.notebook = ttk.Notebook(master=noteBookFrame)
        self.log = tk.Text(master=self.notebook)
        # TreeView
        self.file = ttk.Treeview(master=self.notebook, columns=("A", "B"))
        self.file.heading("#0", text='Item')
        self.file.heading("#1", text='Max Times')
        self.file.heading("#2", text='Modification Date')
        self.file.column('#0', anchor="c", stretch=tk.YES)
        self.file.column("#1", anchor="c", stretch=tk.YES)
        self.file.column('#2', anchor="c", stretch=tk.YES)
        self.file.bind('<Double-1>', self.open_file)
        # Menu
        self.menu = tk.Menu(self.file, tearoff=0)
        self.menu.add_command(label="open", command=self.open_file_menu)
        self.menu.add_separator()
        self.menu.add_command(label="delete", command=self.delete_file)
        self.file.bind('<Button-3>', self.show_menu)
        self.notebook.add(self.log, text="Output")
        self.notebook.add(self.file, text="File")
        self.notebook.pack(fill='both', expand=YES)
        noteBookFrame.pack(fill='both', expand=YES)

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def choose_image(self, event):
        index = int(self.image_v.get())
        if (index <= 124 and index >= 1):
            index = index - 1
            self.images_index = index
            self.canvasImage.itemconfig(self.image_on_canvas, image=self.my_images[index])
        else:
            message = 'Error: 1<= Index <=124\n'
            self.message('outofrange', message, 0, len(message), 'red', False, True)

    def select_all(self, event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')

    def message(self, message_name, message, start, end, color, underline, is_open):
        if is_open == False:
            self.log.insert('1.0', message)
        else:
            self.log.insert('1.0', message)
            self.log.tag_add(message_name, '1.' + str(start), '1.' + str(end))
            self.log.tag_config(message_name, foreground=color, underline=underline)

    def next_image(self):
        if self.images_index < 123:
            self.images_index = int(self.image_v.get())
            self.image_v.set(str(self.images_index + 1))
            self.canvasImage.itemconfig(self.image_on_canvas, image=self.my_images[self.images_index])
        else:
            message = 'Error: 1<= Index <=124\n'
            self.message('outofrange', message, 0, len(message), 'red', False, True)

    def prev_image(self):
        if self.images_index >= 1:
            self.images_index = int(self.image_v.get()) - 1
            self.image_v.set(str(self.images_index))
            self.images_index = self.images_index - 1
            self.canvasImage.itemconfig(self.image_on_canvas, image=self.my_images[self.images_index])
        else:
            message = 'Error: 1<= Index <=124\n'
            self.message('outofrange', message, 0, len(message), 'red', False, True)

    def push_enter(self, event):
        self.thread()

    def delete_file(self):
        try:
            item = self.file.selection()[0]
            fn = self.file.item(item, 'text')
            print (fn)
            if 'linux' in str(sys.platform):
                if fn[-4:] == '.txt':
                    os.remove('../data/' + fn)
                else:
                    os.remove('../video/' + fn)
            elif 'win32' in str(sys.platform):
                if fn[-4:] == '.txt':
                    os.remove('..\\data\\' + fn)
                else:
                    os.remove('..\\video\\' + fn)
            self.file.delete(item)
        except:
            messagebox.showerror("Error", "Error, please choose a item first")

    def open_file_menu(self):
        try:
            item = self.file.selection()[0]
            fn = self.file.item(item, 'text')
            print (fn)
            if 'linux' in str(sys.platform):
                if fn[-4:] == '.txt':
                    subprocess.call(('xdg-open', '../data/' + fn))
                else:
                    subprocess.call(('xdg-open', '../video/' + fn))
            elif 'win32' in str(sys.platform):
                if fn[-4:] == '.txt':
                    os.startfile('..\\data\\' + fn)
                else:
                    os.startfile('..\\video\\' + fn)
        except:
            messagebox.showerror("Error", "Error, please choose a item first")

    def open_file(self, event):
        try:
            item = self.file.selection()[0]
            fn = self.file.item(item, 'text')
            print (fn[-4:])
            if 'linux' in str(sys.platform):
                if fn[-4:] == '.txt':
                    subprocess.call(('xdg-open', '../data/' + fn))
                else:
                    subprocess.call(('xdg-open', '../video/' + fn))
            elif 'win32' in str(sys.platform):
                if fn[-4:] == '.txt':
                    os.startfile('..\\data\\' + fn)
                else:
                    os.startfile('..\\video\\' + fn)
        except:
            messagebox.showerror("Error", "Error, please choose a item first")

    def updateOption(self):
        self.maxtimes = self.v.get()
        message = "Max times has been changed to " + str(self.v.get()) + "\n"
        self.message('changetimes', message, 0, len(message), 'blue', FALSE, True)

    def kill_all(self):
        try:
            self.t1.raise_exception()
            self.t1.threadSign = 0
            message = 'Threads has been Killed\n'
            self.message('killthread', message, 0, len(message), 'blue', FALSE, True)
        except:
            print ("no thread")

    def isRunning(self):
        try:
            if self.t1.isAlive():
                self.answer()
                self.kill_all()
                return TRUE
            else:
                return FALSE
        except:
            print ("no thread")
        return FALSE

    def camera_thread(self):
        self.t = tk.Toplevel(master=self.master)
        self.t.wm_title("Camera")
        self.l = tk.Label(self.t)
        self.l.pack(side="top", fill="both", expand=True)
        fn = self.account.get() + "_" + self.password.get() + ".avi"
        self.t3 = GUI_Camera.Camera(fn=fn, maxtimes=self.maxtimes, l=self.l, t=self.t, file=self.file,
                                    message=self.message)
        self.t3.setDaemon(True)
        self.t3.start()


    def answer(self):
        messagebox.showerror("Error", "Error, Application is running")

    def thread(self):
        if not self.isRunning():
            self.log.delete("1.0", END)
            self.initialTimes = int(self.variable.get()) - 1
            self.t1 = GUI_LeapMotion.LeapRun(account=self.account.get(), password=self.password.get(),
                                             suffix=self.suffix.get(),
                                             times=self.variable.get(),
                                             ax1=self.ax1, ax2=self.ax2,
                                             canvas_draw=self.canvas,
                                             fig=self.fig, log=self.log,
                                             file=self.file, writingTimes=self.writingTimes,
                                             maxtimes=self.maxtimes)
            self.t1.setDaemon(True)
            self.t1.start()

    def writingTimes(self):
        self.initialTimes = self.initialTimes + 1
        if (self.initialTimes == self.maxtimes):
            self.initialTimes = 0
        self.variable.set(self.OPTIONS[self.initialTimes])

    def stop_camera(self, event):
        try:
            self.t3.stop = 1
        except:
            print ("camera is not running")



    # def _quit(self):
    #     print ("application is closed")
    #     app.quit()
    #     app.destroy()
    #     sys.exit()


# if __name__ == '__main__':
#     app = Application()
#     app.protocol("WM_DELETE_WINDOW", app._quit)
#     app.mainloop()
