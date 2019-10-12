import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import serial
import threading
import struct
import datetime
import os



class GloveRun(threading.Thread):

    def __init__(self, account, password, suffix, times, canvas_draw, fig, log, file, writingTimes, maxtimes, ax):
        threading.Thread.__init__(self)
        self.account = account
        self.password = password
        self.times = times
        self.N = 2000
        self.tip_co = np.zeros((self.N, 6), np.float32)
        self.joint_series = np.zeros((self.N, 5, 5, 3), np.float32)
        self.confs = np.zeros((self.N, 1), np.float32)
        self.canvas = canvas_draw
        self.fig = fig
        self.log = log
        self.suffix = suffix
        self.threadSign = 1
        self.file = file
        self.writingTimes = writingTimes
        self.maxtimes = maxtimes
        self.ser = serial.Serial('/dev/ttyACM0', 576000)
        self.ax = ax

    def message(self, message_name, message, start, end, color, underline, is_open):
        if is_open == False:
            self.log.insert('1.0', message)
        else:
            self.log.insert('1.0', message)
            self.log.tag_add(message_name, '1.' + str(start), '1.' + str(end))
            self.log.tag_config(message_name, foreground=color, underline=underline)

    def recv_payload(self, payload_len, serial_dev):

        payload = self.ser.read(payload_len)
        ts = struct.unpack_from('<i', payload[0:4])[0]
        sample = np.frombuffer(payload[4:payload_len], dtype=np.float32)
        print(ts)
        for j in range(12):
            print("%7.4f, " % sample[j])
            self.log.insert('1.0', ("%7.4f\n" % sample[j]))
        print()
        for j in range(12, 24):
            print("%7.4f, " % sample[j])
            self.log.insert('1.0', ("%7.4f\n" % sample[j]))
        print()

        return (ts, sample)


    def run(self):
        # if len(sys.argv) < 2:
        #     print("Missing file name!!!")
        #     exit(0)
        #
        # fn = sys.argv[1]
        print (self.account)
        print (self.password)
        print (self.times)
        print (self.suffix)



        for j in range(12):
            self.ax = self.fig.add_subplot(12, 1, j + 1)
            self.ax.clear()



        if (self.suffix == ""):
            file_suffix = ""
        else:
            file_suffix = self.suffix + "_"
        fn = self.account + "_" + self.password + "_" + file_suffix + str(self.times).zfill(2) + ".txt"
        print(self.ser.name)
        self.log.insert('1.0', self.ser.name + "\n")

        # 0 ---> initial state, expecting magic1 (character 'A', decimal 65, hex 0x41)
        # 1 ---> after magic1 is received, expecting magic2 (character 'F', decimal 70, hex 0x46)
        # 2 ---> after magic2 is received, expecting a length (decimal 100, hex 0x64)
        # 3 ---> after length is received, expecting an opcode (decimal 0, hex 0x00)

        state = 0

        stop_count = 0

        data = np.zeros((2000, 25), np.float32)

        i = 0

        while True:

            s = int(self.ser.read(1).encode('hex'), 16)
            c = s

            if state == 0:
                if c == 65:
                    state = 1
                else:
                    state = 0

            elif state == 1:

                if c == 70:
                    state = 2
                else:
                    state = 0

            elif state == 2:

                if c == 100:
                    state = 3
                else:
                    state = 0


            elif state == 3:

                if c == 0:

                    ts, sample = self.recv_payload(100, self.ser)
                    data[i, 0] = ts
                    data[i, 1:] = sample

                    i += 1

                    # test stop condition

                    amp = sample[3] * sample[3] \
                          + sample[4] * sample[4] \
                          + sample[5] * sample[5]

                    if amp < 3:

                        stop_count += 1
                    else:

                        stop_count = 0

                    if stop_count > 50 or i >= 2000:
                        break

                state = 0

            else:

                print("Unknown state! Program is corrupted!")

        # save data to file
        # CAUTION: throw away the first sample
        data = data[1:i, :]

        data[:, 0] -= data[0, 0]

        np.savetxt('../glove_data/'+fn, data, fmt='%.8f', delimiter=', ')

        self.ser.close()

        # plot

        # fig = plt.figure()

        for j in range(12):
            self.ax = self.fig.add_subplot(12, 1, j + 1)

            self.ax.plot(data[:, 0], data[:, j + 1])

        self.writingTimes()
        self.canvas.draw_idle()

        message = fn + " has been saved successfully\n"
        self.message('filesave', message, 0, len(message), 'purple', False, True)

        message = 'Plot is completed, threads has been killed\n'
        self.message('plotcompleted', message, 0, len(message), 'orange', False, False)

        if (self.file.exists(fn)):
            self.file.delete(fn)
            self.file.insert('', 0, text=fn, iid=fn, values=(str(self.maxtimes), str(datetime.datetime.now())[:-7]))
        else:
            self.file.insert('', 0, text=fn, iid=fn, values=(str(self.maxtimes), str(datetime.datetime.now())[:-7]))



