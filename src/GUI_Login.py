# -*- coding: utf-8
import string
from tkinter import *
from tkinter import ttk
import GUI_Main
import json
import client_ui
import threading
import sys
import SystemChecking
check = SystemChecking.Application()
src_dir, arch_dir = check.system_checking()
check.create_file()
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

        style = ttk.Style()
        style.configure('TLabel', foreground='black')

        accountFrame = Frame(self.fm)
        ttk.Label(master=accountFrame, text="Please input your account:", width=40).pack(fill=X, side=LEFT)
        self.account = ttk.Entry(master=accountFrame)
        self.account.pack(fill=X, side=LEFT)
        accountFrame.pack(fill='both', expand=YES)

        passwordFrame = Frame(self.fm)
        ttk.Label(master=passwordFrame, text="Please input your password:", width=40).pack(fill=X, side=LEFT)
        self.password = ttk.Entry(master=passwordFrame)
        self.password.pack(fill=X, side=LEFT)
        passwordFrame.pack(fill='both', expand=YES)

        # ttk.Button(self.fm, text='Leap Motion', command=self.leap, width=200).pack(side=TOP, fill=BOTH, expand=1)
        # ttk.Button(self.fm, text='Glove', command=self.leap2, width=200).pack(side=TOP, fill=BOTH, expand=1)
        ttk.Button(self.fm, text='Login', command=lambda
                event=None: self.leap3(event), width=200).pack(side=TOP, fill=BOTH, expand=1)
        self.fm.pack(fill=BOTH, expand=YES)
        self.fm.bind_all('<Return>',lambda
                event=None: self.leap3(event))

    def leap(self):
        # self.fm.quit()
        self.fm.destroy()
        GUI_Main.Application(self.master, "1", self.input, check.leap_data_path(), check.video_data_path(),
                             check.glove_data_path())

    def leap2(self):
        # self.fm.quit()
        self.fm.destroy()
        GUI_Main.Application(self.master, "2", self.input, check.glove_data_path(), check.video_data_path(),
                             check.leap_data_path())


    def leap3(self, event):
        # self.fm.quit()
        account = self.account.get()
        password = self.password.get()
        match = False
        with open('../meta/account.json') as f:
            data = json.load(f)
            for p in data:
                for i in p['user']:
                    if(account == i['account'] and password == i['password']):
                        client_id = i['id']
                        lan = i['lan']
                        group_id = i['group']
                        word_id = i['word']
                        self.fm.destroy()
                        GUI_Main.Application(self.master, "3", self.input, check.glove_data_path(),
                                             check.video_data_path(),
                                             check.leap_data_path(), client_id, lan, group_id, word_id, account)
                        match = True
                        break
        if match == False:
            from tkinter import messagebox
            messagebox.showerror("Error", "account and password doesn't match")






    def _quit(self):
        print ("application is closed")
        self.master.quit()
        self.master.destroy()
        sys.exit()


if __name__ == '__main__':

    input = None
    try:

        # import serial.tools.list_ports
        # port_list = list(serial.tools.list_ports.comports())
        # for port in port_list:
        #     print port
        filepath = "../meta/config.txt"
        map = {}
        with open(filepath) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                config_list = line.strip().split(':')
                map[config_list[0]] = config_list[1]
                line = fp.readline()
                cnt += 1
        input = map['port']

    except:
        print ("port error")
        # print ("ports: " + input)
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