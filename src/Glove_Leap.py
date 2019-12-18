import threading
import os, sys, inspect, subprocess
import numpy as np
import SystemChecking
check = SystemChecking.Application()
src_dir, arch_dir = check.system_checking()
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
class Application(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.leap = ClientLeap()
        self.glove = ClientGlove()


    def run(self):
        self.leap.start()
        self.glove.start()



class ClientLeap(threading.Thread):

    def __init__(self, fig1, ax_trajectory_2d, ax_trajectory_3d, client_id, lan_str, ii):
        threading.Thread.__init__(self)

        N = 2000
        self.N = N
        self.ltss = np.zeros((N, 1), np.float64)
        self.tss = np.zeros((N, 1), np.float64)
        self.tip_co = np.zeros((N, 6), np.float32)
        self.hand_co = np.zeros((N, 9), np.float32)
        self.joint_series = np.zeros((N, 5, 5, 3), np.float32)
        self.bone_geo = np.zeros((N, 5, 4, 2), np.float32)
        self.confs = np.zeros((N, 1), np.float32)
        self.valids = np.zeros((N, 1), np.uint32)

        self.t2d = np.zeros((N, 2), np.float32)

        self.has_data = False

        self.stop_flag = False
        self.client_stop = False

        # self.fn = './sample.csv'

        self.controller = Leap.Controller()

        self.fig1 = fig1
        self.ax_trajectory_2d = ax_trajectory_2d
        self.ax_trajectory_3d = ax_trajectory_3d

        self.fn = (check.separator + 'data_leap' + check.single + '%s' + check.single + 'client%s_word%s') % \
                  (lan_str, client_id.split(' ')[1], ii.split(' ')[1])

        # device_list = self.controller.devices

        # assert(len(device_list) > 0)


    def capture(self):

        N = self.N
        controller = self.controller

        # zeroize the arraies
        self.ltss = np.zeros((N, 1), np.float64)
        self.tss = np.zeros((N, 1), np.float64)
        self.tip_co = np.zeros((N, 6), np.float32)
        self.hand_co = np.zeros((N, 9), np.float32)
        self.joint_series = np.zeros((N, 5, 5, 3), np.float32)
        self.bone_geo = np.zeros((N, 5, 4, 2), np.float32)
        self.confs = np.zeros((N, 1), np.float32)
        self.valids = np.zeros((N, 1), np.uint32)

        out_of_range = 0

        self.has_data = False

        init_frame = controller.frame()
        frame_id = init_frame.id

        # wait until the first frame is ready
        while True:

            init_frame = controller.frame()
            if frame_id == init_frame.id:
                continue
            else:
                frame_id = init_frame.id
                break

        frame = init_frame

        # actual length of the finger motion data
        i = -1
        self.l = 0

        while not self.stop_flag:

            # Retrieve a frame
            frame = controller.frame()

            if frame_id == frame.id:
                continue
            else:
                frame_id = frame.id

            if i >= N:
                self.l = N
                break
            else:
                i += 1
                self.l += 1

            # frame_str = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
            #    frame.id - init_frame.id, (frame.timestamp - init_frame.timestamp) / 1000, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
            # print(frame_str)

            self.tss[i] = frame.timestamp
            self.valids[i] = 1

            # Get hands
            if not frame.hands:
                out_of_range += 1
                self.valids[i] = 0
                continue

            self.has_data = True

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
                self.hand_co[i][j] = hand_pos[j]

            # print("\tpitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (direction.pitch * Leap.RAD_TO_DEG, normal.roll * Leap.RAD_TO_DEG, direction.yaw * Leap.RAD_TO_DEG))

            # Get index finger tip
            ifinger = hand.fingers[1]
            tbone = ifinger.bone(3)
            tip_end = tbone.next_joint
            tip_start = tbone.prev_joint
            tip_pos = (tip_end.x, tip_end.y, tip_end.z,
                       tip_end.x - tip_start.x, tip_end.y - tip_start.y, tip_end.z - tip_start.z)

            for j in range(6):
                self.tip_co[i, j] = tip_pos[j]

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
                    self.bone_geo[i][j][k][0] = bone_length
                    self.bone_geo[i][j][k][1] = bone_width


        self.l = self.l - 1
        print('capture stopped')
        print("# of frames: %d, last ts: %d, out of range: %d" % \
              (self.l, self.tss[self.l - 1], out_of_range))

    def project(self):

        self.t2d = np.zeros((self.N, 2))

        if not self.has_data:
            return

        t3d = self.tip_co[:, 0:3].copy()
        t3d[:, 0] = self.tip_co[:, 2]
        t3d[:, 1] = self.tip_co[:, 0]
        t3d[:, 2] = self.tip_co[:, 1]

        v3d = self.tip_co[:, 3:6].copy()
        v3d[:, 0] = self.tip_co[:, 5]
        v3d[:, 1] = self.tip_co[:, 3]
        v3d[:, 2] = self.tip_co[:, 4]

        v = np.mean(v3d, axis=0)
        nv = np.linalg.norm(v)
        v /= nv

        up = np.asarray((0, 0, 1), dtype=np.float32)

        x_axis = -v
        y_axis = np.cross(up, x_axis)
        y_axis = y_axis / np.linalg.norm(y_axis)
        z_axis = np.cross(x_axis, y_axis)
        z_axis = z_axis / np.linalg.norm(z_axis)

        x_axis = x_axis.reshape((1, 3))
        y_axis = y_axis.reshape((1, 3))
        z_axis = z_axis.reshape((1, 3))

        R = np.concatenate((x_axis, y_axis, z_axis))

        pt3d = np.matmul(R, t3d.transpose())

        pt3d = pt3d.transpose()

        # print(x_axis, y_axis, z_axis)

        self.t2d = pt3d[:, 1:3]


    def save_to_file(self, fn):

        fd = open(fn, 'w')
        for i in range(0, self.l):

            tip = tuple(self.tip_co[i])
            hand = tuple(self.hand_co[i])
            confidence = self.confs[i]
            valid = self.valids[i]
            ts = self.tss[i]

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
                    bgeo = tuple(self.bone_geo[i][j][k])

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



    def run(self):

        print('client_leap started.')

        while not self.client_stop:

            if self.client_stop:
                break

            print('run once' + self.fn)

            self.capture()

            self.save_to_file(self.fn)

        self.update_trajectory()

        print('client_leap closed.')



    def update_trajectory(self):
        x = 1
        if x == 1:
            # self.c_leap.project()
            self.project()
            # t2d = self.c_leap.t2d
            t2d = self.t2d
            # tip_co = self.c_leap.tip_co
            tip_co = self.tip_co
            # l = self.c_leap.l
            l = self.l

            self.ax_trajectory_2d.clear()
            self.ax_trajectory_2d.plot(t2d[1:l - 1, 0], t2d[1:l - 1, 1])
            self.ax_trajectory_2d.set_xlim(-300, 300)
            self.ax_trajectory_2d.set_ylim(0, 600)

            self.ax_trajectory_3d.clear()
            self.ax_trajectory_3d.plot(tip_co[:l, 2], tip_co[:l, 0], tip_co[:l, 1])
            self.ax_trajectory_3d.set_xlim(-300, 300)
            self.ax_trajectory_3d.set_ylim(-300, 300)
            self.ax_trajectory_3d.set_zlim(0, 600)


            self.fig1.canvas.draw_idle()




class ClientGlove(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_flag = False
        self.client_stop = False
        self.sem = threading.Semaphore(0)
        self.fn = './sample.csv'
        import serial.tools.list_ports
        port_list = list(serial.tools.list_ports.comports())
        print(port_list[0])
        self.ser = serial.Serial('COM3', 57600)

        self.data = np.zeros((2000, 33), np.float32)
        self.l = 0

    def capture_start(self, fn):

        self.fn = fn
        self.stop_flag = False

        self.sem.release()

    def capture_stop(self):

        self.stop_flag = True

    def close(self):

        self.client_stop = True
        self.sem.release()

    def recv_payload(self, payload_len, ser):

        # print(payload_len)

        payload = ser.read(payload_len)

        # print(payload)

        ts = np.frombuffer(payload[0:4], dtype=np.int32)[0]

        sample = np.frombuffer(payload[4:payload_len], dtype=np.float32)

        return (ts, sample)

    def capture(self):

        N = 2000

        # 0 ---> initial state, expecting magic1 (character 'D', decimal 68, hex 0x44)
        # 1 ---> after magic1 is received, expecting magic2 (character 'L', decimal 76, hex 0x4C)
        # 2 ---> after magic2 is received, expecting a length (decimal 132, hex 0x84)
        # 3 ---> after length is received, expecting an opcode (decimal 133, hex 0x85)

        state = 0

        self.data = np.zeros((N, 33), np.float32)

        i = 0
        msg_len = 0

        self.ser.reset_input_buffer()

        while not self.stop_flag:
            s = self.ser.read(1)

            # cast the received byte to an integer
            c = s[0]

            # print(c)

            if state == 0:

                if c == 'D':  # ASCII 68 is 'D'
                    state = 1
                else:
                    state = 0

            elif state == 1:

                if c == 'L':  # ASCII 76 is 'L'
                    state = 2
                else:
                    state = 0

            elif state == 2:

                msg_len = c
                state = 3


            elif state == 3:

                # if c == 133:

                ts, sample = self.recv_payload(132, self.ser)
                self.data[i, 0] = ts
                self.data[i, 1:] = sample

                i += 1
                self.l = i

                if i >= N:
                    break

                state = 0

            else:

                print("Unknown state! Program is corrupted!")

        print(self.l)

    def save_to_file(self, fn):

        np.savetxt(fn, self.data, fmt='%.8f', delimiter=', ')

    def run(self):

        print('client_glove started.')

        while not self.client_stop:
            # self.sem.acquire()
            if self.client_stop:
                break

            print('run once' + self.fn)

            self.capture()

            self.save_to_file(self.fn)

        print('client_glove closed.')

        self.ser.close()

