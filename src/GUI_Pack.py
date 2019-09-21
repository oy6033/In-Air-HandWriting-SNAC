import datetime
import time
import matplotlib

matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from PIL import ImageTk
import PIL.Image
import Tkinter as tk
from Tkinter import *
import ttk
from tkMessageBox import *
import os, sys, inspect, subprocess

if not os.path.exists('../data'):
    os.makedirs('../data')
import threading
import ctypes

# Leap Instantiation
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
if 'linux' in str(sys.platform):
    arch_dir = '../lib_Linux/x64' if sys.maxsize > 2 ** 32 else '../lib_Linux/x86'
elif 'win32' in str(sys.platform):
    arch_dir = '../lib_Windows/x64' if sys.maxsize > 2 ** 32 else '../lib_Windows/x86'
elif 'darwin' in str(sys.platform):
    arch_dir = '../lib_Mac' if sys.maxsize > 2 ** 32 else '../lib_Mac'
else:
    sys.exit()
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap


class LeapRun(threading.Thread):

    def __init__(self, account, password, suffix, times, ax1, ax2, canvas_draw, fig, log):
        threading.Thread.__init__(self)
        self.account = account
        self.password = password
        self.times = times
        self.N = 2000
        self.tip_co = np.zeros((self.N, 6), np.float32)
        self.joint_series = np.zeros((self.N, 5, 5, 3), np.float32)
        self.confs = np.zeros((self.N, 1), np.float32)
        self.ax1 = ax1
        self.ax2 = ax2
        self.canvas = canvas_draw
        self.fig = fig
        self.log = log
        self.suffix = suffix
        self.threadSign = 1

    def plot2(self):
        self.ax2.cla()
        # plot hand geometry
        joints = self.joint_series[0]

        for i in range(self.N):

            if self.confs[i] > 0.5:
                joints = self.joint_series[i]
                break
        # print(joints)
        x2 = []
        y2 = []
        z2 = []
        for j in range(5):
            for k in range(5):
                x2.append(joints[j][k][0])
                y2.append(joints[j][k][1])
                z2.append(joints[j][k][2])
            for k in range(4, -1, -1):
                x2.append(joints[j][k][0])
                y2.append(joints[j][k][1])
                z2.append(joints[j][k][2])

        # CAUTION: axis mapping: x -> y, y -> z, z -> x
        xs2 = z2
        ys2 = x2
        zs2 = y2

        self.ax2.plot(xs2, ys2, zs2)

        self.ax2.set_xlim3d(-200, 200)
        self.ax2.set_ylim3d(-200, 200)
        self.ax2.set_zlim3d(0, 600)

        self.ax2.set_xlabel('X')
        self.ax2.set_ylabel('Y')
        self.ax2.set_zlabel('Z')
        self.canvas.draw_idle()

    def plot1(self):
        # plot trajectory of finger tip
        # CAUTION: axis mapping: x -> y, y -> z, z -> x
        self.ax1.clear()
        ys1 = [pos[0] for pos in self.tip_co]
        zs1 = [pos[1] for pos in self.tip_co]
        xs1 = [pos[2] for pos in self.tip_co]

        self.ax1.scatter(xs1, ys1, zs1, s=0.2)

        self.ax1.set_xlim3d(-500, 500)
        self.ax1.set_ylim3d(-500, 500)
        self.ax1.set_zlim3d(0, 600)

        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        self.ax1.set_zlabel('Z')
        self.canvas.draw_idle()
        # self.writingTimes()

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def message(self, message_name, message, start, end, color, underline, is_open):
        if is_open == FALSE:
            self.log.insert('1.0', message)
        else:
            self.log.insert('1.0', message)
            self.log.tag_add(message_name, '1.' + str(start), '1.' + str(end))
            self.log.tag_config(message_name, foreground=color, underline=underline)

    def realTimePlot(self):
        # only run once
        while (1):
            t = threading.Thread(target=self.plot1)
            t.setDaemon(True)
            t.start()
            t.join()
            time.sleep(0.8)
            if self.threadSign == 0:
                break

        self.plot2()

        if t.isAlive():
            print self.log.insert('1.0', "Error, thread is not killed, please check\n")
        else:
            message = 'Plot is completed, threads has been killed\n'
            self.message('plotcompleted', message, 0, len(message), 'orange', FALSE, FALSE)

    def run(self):
        print self.account
        print self.password
        print self.times
        print self.suffix

        # N = 2000
        # if len(sys.argv) < 2:
        #     print("Missing dumping file name!!!")
        #     exit(0)
        if (self.suffix == ""):
            file_suffix = ""
        else:
            file_suffix = self.suffix + "_"
        fn = self.account + "_" + self.password + "_" + file_suffix + str(self.times).zfill(2) + ".txt"

        finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']

        controller = Leap.Controller()

        init_frame = controller.frame()
        frame_id = init_frame.id

        # wait until the first frame is ready
        while True:
            if self.threadSign == 0:
                break
            init_frame = controller.frame()
            if frame_id == init_frame.id:
                continue
            else:
                frame_id = init_frame.id
                break

        t2 = threading.Thread(target=self.realTimePlot)
        t2.setDaemon(True)
        t2.start()

        frame = init_frame

        frame_str = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
            frame.id - init_frame.id, (frame.timestamp - init_frame.timestamp) / 1000, len(frame.hands),
            len(frame.fingers), len(frame.tools), len(frame.gestures()))
        print(frame_str)

        self.log.insert('1.0', frame_str + "\n")

        # sensor data
        # CAUTION: preallocate array space for speed
        tss = np.zeros((self.N, 1), np.uint64)
        # tip_co = np.zeros((N, 6), np.float32)
        hand_co = np.zeros((self.N, 9), np.float32)
        # joint_series = np.zeros((N, 5, 5, 3), np.float32)
        bone_geo = np.zeros((self.N, 5, 4, 2), np.float32)
        # confs = np.zeros((N, 1), np.float32)
        valids = np.zeros((self.N, 1), np.uint32)

        # sensor data statistics
        out_of_range = 0

        # termination counter
        tcount = 0

        # termination timestamp
        ts0 = time.time()

        # actual length of the finger motion data
        l = 0
        i = -1

        while True:

            # Retrieve a frame
            frame = controller.frame()

            if frame_id == frame.id:
                continue
            else:
                frame_id = frame.id

            i += 1
            if i >= self.N:
                l = self.N
                break
            if self.threadSign == 0:
                break

            frame_str = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
                frame.id - init_frame.id, (frame.timestamp - init_frame.timestamp) / 1000, len(frame.hands),
                len(frame.fingers), len(frame.tools), len(frame.gestures()))
            print(frame_str)

            self.log.insert('1.0', frame_str + "\n")

            # catch index out of range
            try:
                tss[i] = frame.timestamp
            except IndexError:
                self.log.insert('1.0', "ts array index out of range\n")
                app.kill_all()

            valids[i] = 1

            # Get hands
            if not frame.hands:
                out_of_range += 1
                valids[i] = 0
                continue

            hand = frame.hands[0]

            # Get estimation confidence
            self.confs[i] = hand.confidence

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            hand_pos = (hand.palm_position.x, hand.palm_position.y, hand.palm_position.z,
                        direction.pitch, direction.roll, direction.yaw,
                        normal.pitch, normal.roll, normal.yaw)

            for j in range(9):
                hand_co[i][j] = hand_pos[j]

            # print("\tpitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (direction.pitch * Leap.RAD_TO_DEG, normal.roll * Leap.RAD_TO_DEG, direction.yaw * Leap.RAD_TO_DEG))

            # Get index finger tip
            ifinger = hand.fingers[1]
            tbone = ifinger.bone(3)
            tip_end = tbone.next_joint
            tip_start = tbone.prev_joint
            tip_pos = (tip_end.x, tip_end.y, tip_end.z,
                       tip_end.x - tip_start.x, tip_end.y - tip_start.y, tip_end.z - tip_start.z)

            for j in range(6):
                self.tip_co[i][j] = tip_pos[j]

            # Get fingers
            for j in range(5):

                finger = hand.fingers[j]

                # print("\t\t%s finger, id: %d, length: %fmm, width: %fmm" % (finger_names[finger.type], finger.id, finger.length, finger.width))

                # Get bones and joints

                bone = finger.bone(0)
                bone_start = bone.prev_joint.to_tuple()

                for v in range(3):
                    self.joint_series[i][j][0][v] = bone_start[v]

                for k in range(4):
                    bone = finger.bone(k)
                    bone_pos = bone.next_joint.to_tuple()
                    # print("\t\t\tBone: %s, start: %s, end: %s, direction: %s" % (bone_names[bone.type], bone.prev_joint, bone.next_joint, bone.direction))
                    for v in range(3):
                        self.joint_series[i][j][k + 1][v] = bone_pos[v]
                    bone_length = bone.length
                    bone_width = bone.width
                    bone_geo[i][j][k][0] = bone_length
                    bone_geo[i][j][k][1] = bone_width

            # Early termination if no movement is detected

            if i < 2:
                continue
            else:

                tip_pos_last = self.tip_co[i - 1]
                diff = (tip_pos[0] - tip_pos_last[0]) ** 2 + (tip_pos[1] - tip_pos_last[1]) ** 2 + (
                        tip_pos[2] - tip_pos_last[2]) ** 2

                if diff < 20:
                    tcount += 1
                else:
                    tcount = 0

            if tcount > 100:
                l = i + 1
                break

        # dump sensor data to file
        print_range = "# of frames: %d, last ts: %d, out of range: %d\n" % (l, tss[l - 1], out_of_range)
        if out_of_range > 5:
            self.message('showrange', print_range, print_range.find("out"), len(print_range), 'red', False, True)
            pass
        else:
            self.message('showrange', print_range, print_range.find("out"), len(print_range), 'blue', False, True)
            app.writingTimes()
        print("# of frames: %d, last ts: %d, out of range: %d" % (l, tss[l - 1], out_of_range))

        fd = open('../data/' + fn, 'w')
        for i in range(0, l):

            tip = tuple(self.tip_co[i])
            hand = tuple(hand_co[i])
            confidence = self.confs[i]
            valid = valids[i]
            ts = tss[i]

            # tip contains three positions and three orientations of the finger tip
            tip_str = "%8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f" % tip

            # hand contains three positions, three hand directions, and three normal vector of the center of the hand
            hand_str = "%8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f" % hand

            # one hand contains five fingers, each with positions of five joints, in total 25 3D vectors
            finger_strs = []
            bgeo_strs = []

            for j in range(5):

                for k in range(5):
                    joint = tuple(self.joint_series[i][j][k])

                    joint_str = "%8.04f, %8.04f, %8.04f" % joint
                    finger_strs.append(joint_str)

            for j in range(5):

                for k in range(4):
                    bgeo = tuple(bone_geo[i][j][k])

                    bgeo_str = "%8.04f, %8.04f" % bgeo
                    bgeo_strs.append(bgeo_str)

            fd.write('%d' % ts)
            fd.write(',\t')
            fd.write(tip_str)
            fd.write(',\t\t')
            fd.write(hand_str)
            fd.write(',\t\t')

            for joint_str in finger_strs:
                fd.write(joint_str)
                fd.write(',\t')

            for bgeo_str in bgeo_strs:
                fd.write(bgeo_str)
                fd.write(',\t')

            fd.write("%8.04f,\t" % confidence)
            fd.write("%d" % valid)

            fd.write("\n")

        fd.flush()
        fd.close()
        self.threadSign = 0
        message = fn + " has been saved successfully\n"
        self.message('filesave', message, 0, len(message), 'purple', False, True)

        if(app.file.exists(fn)):
            app.file.delete(fn)
            app.file.insert('', 0, text=fn, iid=fn,values=(str(app.maxtimes), str(datetime.datetime.now())))
        else:
            app.file.insert('', 0, text=fn, iid=fn, values=(str(app.maxtimes), str(datetime.datetime.now())))
        app.file.bind('<Double-1>', app.open_file)
        # app.plot(self.tip_co, self.joint_series, self.confs, self.N)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.maxtimes = 5
        self.wm_title("In-Air Hand Writing")
        self.createWidgets()

    def createWidgets(self):
        mianFram = Frame(master=self)
        mianFram.pack(fill='both', expand=YES)
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
        w.bind("<Return>", self.choose_image)
        comboboxFrame.pack(fill='both', expand=YES)

        nextButtonFrame = tk.Frame(master=imageFrame)
        ttk.Button(master=nextButtonFrame, text='Prev', command=self.prev_image).pack(fill=X, side=LEFT, expand=YES)
        ttk.Button(master=nextButtonFrame, text='Next', command=self.next_image).pack(fill=X, side=LEFT, expand=YES)
        nextButtonFrame.pack(fill='both', expand=YES)
        imageFrame.pack(fill='both', expand=YES)

        accountFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=accountFrame, text="Please input your account:", width=40).pack(fill=X, side=LEFT)
        self.account = ttk.Entry(master=accountFrame, width=40)
        self.account.bind('<Return>', self.push_enter)
        self.account.bind('<Control-KeyRelease-a>', self.select_all)
        self.account.pack(fill=X, side=RIGHT)
        accountFrame.pack(fill='both', expand=YES)

        writingFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=writingFrame, text="Please input your writing word:", width=40).pack(fill=X, side=LEFT)
        self.password = ttk.Entry(master=writingFrame, width=40)
        self.password.bind('<Return>', self.push_enter)
        self.password.bind('<Control-KeyRelease-a>', self.select_all)
        self.password.pack(fill=X, side=RIGHT)
        writingFrame.pack(fill='both', expand=YES)

        suffixFrame = tk.Frame(master=inputFrame)
        ttk.Label(master=suffixFrame, text="Please input suffix if needed:", width=40).pack(fill=X, side=LEFT)
        self.suffix = ttk.Entry(master=suffixFrame, width=40)
        self.suffix.bind('<Return>', self.push_enter)
        self.suffix.bind('<Control-KeyRelease-a>', self.select_all)
        self.suffix.pack(fill=X, side=RIGHT)
        suffixFrame.pack(fill='both', expand=YES)

        dropListFrame = tk.Frame(master=inputFrame)
        self.OPTIONS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.initialTimes = 0
        self.variable = StringVar(master=dropListFrame)
        self.variable.set(self.OPTIONS[self.initialTimes])
        ttk.Label(master=dropListFrame, text="Writing Times:", width=40).pack(fill=X, side=LEFT)
        dropList = apply(tk.OptionMenu, (dropListFrame, self.variable) + tuple(self.OPTIONS))
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

        buttonFrame = tk.Frame(master=inputFrame)

        ttk.Button(master=buttonFrame, text='Draw', command=self.thread).pack(fill=X, side=LEFT, expand=YES)

        ttk.Button(master=buttonFrame, text='Kill All', command=self.kill_all).pack(fill=X, side=LEFT, expand=YES)
        buttonFrame.pack(fill='both', expand=YES)

        noteBookFrame = tk.Frame(master=inputFrame)
        self.notebook = ttk.Notebook(master=noteBookFrame)
        self.log = tk.Text(master=self.notebook)
        self.file = ttk.Treeview(master=self.notebook, columns=("A", "B"))
        self.file.heading("#0", text='Item')
        self.file.heading("#1", text='Writing Times')
        self.file.heading("#2", text='Modification Date')
        self.file.column('#0', anchor="c", stretch=tk.YES)
        self.file.column("#1", anchor="c", stretch=tk.YES)
        self.file.column('#2', anchor="c", stretch=tk.YES)
        self.notebook.add(self.log, text="Output")
        self.notebook.add(self.file, text="File")
        self.notebook.pack(fill='both', expand=YES)
        noteBookFrame.pack(fill='both', expand=YES)

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
        event.widget.select_range(0,'end')
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

    def open_file(self, event):
        item = self.file.selection()[0]
        print self.file.item(item, 'text')
        if 'linux' in str(sys.platform):
            subprocess.call(('xdg-open', '../data/' + self.file.item(item, 'text')))

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
            print "no thread"

    def isRunning(self):
        try:
            if self.t1.isAlive():
                self.answer()
                self.kill_all()
                return TRUE
            else:
                return FALSE
        except:
            print "no thread"
        return FALSE

    def answer(self):
        showerror("Error", "Error, Application is running")

    def thread(self):
        if not self.isRunning():
            self.log.delete("1.0", END)
            self.initialTimes = int(self.variable.get()) - 1
            self.t1 = LeapRun(account=self.account.get(), password=self.password.get(), suffix=self.suffix.get(),
                              times=self.variable.get(),
                              ax1=self.ax1, ax2=self.ax2, canvas_draw=self.canvas, fig=self.fig, log=self.log)
            self.t1.setDaemon(True)
            self.t1.start()

    def writingTimes(self):
        self.initialTimes = self.initialTimes + 1
        if (self.initialTimes == self.maxtimes):
            self.initialTimes = 0
        self.variable.set(self.OPTIONS[self.initialTimes])


def _quit():
    print "application is closed"
    app.quit()
    app.destroy()
    sys.exit()


if __name__ == '__main__':
    app = Application()
    app.protocol("WM_DELETE_WINDOW", _quit)
    app.mainloop()
