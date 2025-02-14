# import threading
# import numpy as np
# import ctypes
# import time
# import os, sys, inspect, subprocess
# import datetime
# import SystemChecking
# check = SystemChecking.Application()
# src_dir, arch_dir = check.system_checking()
# sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
# import Leap
#
#
# class LeapRun(threading.Thread):
#
#     def __init__(self, account, password, suffix, times, ax1, ax2, canvas_draw, fig, log, file, writingTimes, maxtimes, killAll , data_path):
#         threading.Thread.__init__(self)
#         self.account = account
#         self.password = password
#         self.times = times
#         self.N = 2000
#         self.tip_co = np.zeros((self.N, 6), np.float32)
#         self.joint_series = np.zeros((self.N, 5, 5, 3), np.float32)
#         self.confs = np.zeros((self.N, 1), np.float32)
#         self.ax1 = ax1
#         self.ax2 = ax2
#         self.canvas = canvas_draw
#         self.fig = fig
#         self.log = log
#         self.suffix = suffix
#         self.threadSign = 1
#         self.file = file
#         self.writingTimes = writingTimes
#         self.maxtimes = maxtimes
#         self.killAll = killAll
#         self.data_path = data_path
#
#     def plot2(self):
#         self.ax2.cla()
#         # plot hand geometry
#         joints = self.joint_series[0]
#
#         for i in range(self.N):
#
#             if self.confs[i] > 0.5:
#                 joints = self.joint_series[i]
#                 break
#         # print(joints)
#         x2 = []
#         y2 = []
#         z2 = []
#         for j in range(5):
#             for k in range(5):
#                 x2.append(joints[j][k][0])
#                 y2.append(joints[j][k][1])
#                 z2.append(joints[j][k][2])
#             for k in range(4, -1, -1):
#                 x2.append(joints[j][k][0])
#                 y2.append(joints[j][k][1])
#                 z2.append(joints[j][k][2])
#
#         # CAUTION: axis mapping: x -> y, y -> z, z -> x
#         xs2 = z2
#         ys2 = x2
#         zs2 = y2
#
#         self.ax2.plot(xs2, ys2, zs2)
#
#         self.ax2.set_xlim3d(-200, 200)
#         self.ax2.set_ylim3d(-200, 200)
#         self.ax2.set_zlim3d(0, 600)
#
#         self.ax2.set_xlabel('X')
#         self.ax2.set_ylabel('Y')
#         self.ax2.set_zlabel('Z')
#         self.canvas.draw_idle()
#
#     def plot1(self):
#         # plot trajectory of finger tip
#         # CAUTION: axis mapping: x -> y, y -> z, z -> x
#         self.ax1.clear()
#         ys1 = [pos[0] for pos in self.tip_co]
#         zs1 = [pos[1] for pos in self.tip_co]
#         xs1 = [pos[2] for pos in self.tip_co]
#
#         self.ax1.scatter(xs1, ys1, zs1, s=0.2)
#
#         self.ax1.set_xlim3d(-500, 500)
#         self.ax1.set_ylim3d(-500, 500)
#         self.ax1.set_zlim3d(0, 600)
#
#         self.ax1.set_xlabel('X')
#         self.ax1.set_ylabel('Y')
#         self.ax1.set_zlabel('Z')
#         self.canvas.draw_idle()
#         # self.writingTimes()
#
#     def get_id(self):
#         # returns id of the respective thread
#         if hasattr(self, '_thread_id'):
#             return self._thread_id
#         for id, thread in threading._active.items():
#             if thread is self:
#                 return id
#
#     def raise_exception(self):
#         thread_id = self.get_id()
#         res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
#                                                          ctypes.py_object(SystemExit))
#         if res > 1:
#             ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
#             print('Exception raise failure')
#
#     def message(self, message_name, message, start, end, color, underline, is_open):
#         if is_open == False:
#             self.log.insert('1.0', message)
#         else:
#             self.log.insert('1.0', message)
#             self.log.tag_add(message_name, '1.' + str(start), '1.' + str(end))
#             self.log.tag_config(message_name, foreground=color, underline=underline)
#
#     def realTimePlot(self):
#         # only run once
#         while (1):
#             t = threading.Thread(target=self.plot1)
#             t.setDaemon(True)
#             t.start()
#             t.join()
#             time.sleep(0.8)
#             if self.threadSign == 0:
#                 break
#
#         self.plot2()
#
#         if t.isAlive():
#             print (self.log.insert('1.0', "Error, thread is not killed, please check\n"))
#         else:
#             message = 'Plot is completed, threads has been killed\n'
#             self.message('plotcompleted', message, 0, len(message), 'orange', False, False)
#
#     def run(self):
#         print (self.account)
#         print (self.password)
#         print (self.times)
#         print (self.suffix)
#
#         # N = 2000
#         # if len(sys.argv) < 2:
#         #     print("Missing dumping file name!!!")
#         #     exit(0)
#         if (self.suffix == ""):
#             file_suffix = ""
#         else:
#             file_suffix = self.suffix + "_"
#         fn = self.account + "_" + self.password + "_" + file_suffix + str(self.times).zfill(2) + ".txt"
#
#         finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
#         bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
#
#         controller = Leap.Controller()
#
#         init_frame = controller.frame()
#         frame_id = init_frame.id
#
#         # wait until the first frame is ready
#         while True:
#             if self.threadSign == 0:
#                 break
#             init_frame = controller.frame()
#             if frame_id == init_frame.id:
#                 continue
#             else:
#                 frame_id = init_frame.id
#                 break
#
#         t2 = threading.Thread(target=self.realTimePlot)
#         t2.setDaemon(True)
#         t2.start()
#
#         frame = init_frame
#
#         frame_str = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#             frame.id - init_frame.id, (frame.timestamp - init_frame.timestamp) / 1000, len(frame.hands),
#             len(frame.fingers), len(frame.tools), len(frame.gestures()))
#         print(frame_str)
#
#         # GUI_Login.Application().go_main.log.insert('1.0', frame_str + "\n")
#         self.log.insert('1.0', frame_str + "\n")
#
#         # sensor data
#         # CAUTION: preallocate array space for speed
#         tss = np.zeros((self.N, 1), np.uint64)
#         # tip_co = np.zeros((N, 6), np.float32)
#         hand_co = np.zeros((self.N, 9), np.float32)
#         # joint_series = np.zeros((N, 5, 5, 3), np.float32)
#         bone_geo = np.zeros((self.N, 5, 4, 2), np.float32)
#         # confs = np.zeros((N, 1), np.float32)
#         valids = np.zeros((self.N, 1), np.uint32)
#
#         # sensor data statistics
#         out_of_range = 0
#
#         # termination counter
#         tcount = 0
#
#         # termination timestamp
#         ts0 = time.time()
#
#         # actual length of the finger motion data
#         l = 0
#         i = -1
#
#         while True:
#
#             # Retrieve a frame
#             frame = controller.frame()
#
#             if frame_id == frame.id:
#                 continue
#             else:
#                 frame_id = frame.id
#
#             i += 1
#             if i >= self.N:
#                 l = self.N
#                 break
#             if self.threadSign == 0:
#                 break
#
#             frame_str = "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#                 frame.id - init_frame.id, (frame.timestamp - init_frame.timestamp) / 1000, len(frame.hands),
#                 len(frame.fingers), len(frame.tools), len(frame.gestures()))
#             print(frame_str)
#
#             self.log.insert('1.0', frame_str + "\n")
#
#             # catch index out of range
#             try:
#                 tss[i] = frame.timestamp
#             except IndexError:
#                 self.log.insert('1.0', "ts array index out of range\n")
#                 self.killAll()
#
#             valids[i] = 1
#
#             # Get hands
#             if not frame.hands:
#                 out_of_range += 1
#                 valids[i] = 0
#                 continue
#
#             hand = frame.hands[0]
#
#             # Get estimation confidence
#             self.confs[i] = hand.confidence
#
#             # Get the hand's normal vector and direction
#             normal = hand.palm_normal
#             direction = hand.direction
#
#             hand_pos = (hand.palm_position.x, hand.palm_position.y, hand.palm_position.z,
#                         direction.pitch, direction.roll, direction.yaw,
#                         normal.pitch, normal.roll, normal.yaw)
#
#             for j in range(9):
#                 hand_co[i][j] = hand_pos[j]
#
#             # print("\tpitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (direction.pitch * Leap.RAD_TO_DEG, normal.roll * Leap.RAD_TO_DEG, direction.yaw * Leap.RAD_TO_DEG))
#
#             # Get index finger tip
#             ifinger = hand.fingers[1]
#             tbone = ifinger.bone(3)
#             tip_end = tbone.next_joint
#             tip_start = tbone.prev_joint
#             tip_pos = (tip_end.x, tip_end.y, tip_end.z,
#                        tip_end.x - tip_start.x, tip_end.y - tip_start.y, tip_end.z - tip_start.z)
#
#             for j in range(6):
#                 self.tip_co[i][j] = tip_pos[j]
#
#             # Get fingers
#             for j in range(5):
#
#                 finger = hand.fingers[j]
#
#                 # print("\t\t%s finger, id: %d, length: %fmm, width: %fmm" % (finger_names[finger.type], finger.id, finger.length, finger.width))
#
#                 # Get bones and joints
#
#                 bone = finger.bone(0)
#                 bone_start = bone.prev_joint.to_tuple()
#
#                 for v in range(3):
#                     self.joint_series[i][j][0][v] = bone_start[v]
#
#                 for k in range(4):
#                     bone = finger.bone(k)
#                     bone_pos = bone.next_joint.to_tuple()
#                     # print("\t\t\tBone: %s, start: %s, end: %s, direction: %s" % (bone_names[bone.type], bone.prev_joint, bone.next_joint, bone.direction))
#                     for v in range(3):
#                         self.joint_series[i][j][k + 1][v] = bone_pos[v]
#                     bone_length = bone.length
#                     bone_width = bone.width
#                     bone_geo[i][j][k][0] = bone_length
#                     bone_geo[i][j][k][1] = bone_width
#
#             # Early termination if no movement is detected
#
#             if i < 2:
#                 continue
#             else:
#
#                 tip_pos_last = self.tip_co[i - 1]
#                 diff = (tip_pos[0] - tip_pos_last[0]) ** 2 + (tip_pos[1] - tip_pos_last[1]) ** 2 + (
#                         tip_pos[2] - tip_pos_last[2]) ** 2
#
#                 if diff < 20:
#                     tcount += 1
#                 else:
#                     tcount = 0
#
#             if tcount > 100:
#                 l = i + 1
#                 break
#
#         # dump sensor data to file
#         print_range = "# of frames: %d, last ts: %d, out of range: %d\n" % (l, tss[l - 1], out_of_range)
#         if out_of_range > 5:
#             self.message('showrange', print_range, print_range.find("out"), len(print_range), 'red', False, True)
#             pass
#         else:
#             self.message('showrange', print_range, print_range.find("out"), len(print_range), 'blue', False, True)
#             if(self.threadSign == 1):
#                 self.writingTimes()
#         print("# of frames: %d, last ts: %d, out of range: %d" % (l, tss[l - 1], out_of_range))
#
#         fd = open(self.data_path + fn, 'w')
#         for i in range(0, l):
#
#             tip = tuple(self.tip_co[i])
#             hand = tuple(hand_co[i])
#             confidence = self.confs[i]
#             valid = valids[i]
#             ts = tss[i]
#
#             # tip contains three positions and three orientations of the finger tip
#             tip_str = "%8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f" % tip
#
#             # hand contains three positions, three hand directions, and three normal vector of the center of the hand
#             hand_str = "%8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f, %8.04f" % hand
#
#             # one hand contains five fingers, each with positions of five joints, in total 25 3D vectors
#             finger_strs = []
#             bgeo_strs = []
#
#             for j in range(5):
#
#                 for k in range(5):
#                     joint = tuple(self.joint_series[i][j][k])
#
#                     joint_str = "%8.04f, %8.04f, %8.04f" % joint
#                     finger_strs.append(joint_str)
#
#             for j in range(5):
#
#                 for k in range(4):
#                     bgeo = tuple(bone_geo[i][j][k])
#
#                     bgeo_str = "%8.04f, %8.04f" % bgeo
#                     bgeo_strs.append(bgeo_str)
#
#             fd.write('%d' % ts)
#             fd.write(',\t')
#             fd.write(tip_str)
#             fd.write(',\t\t')
#             fd.write(hand_str)
#             fd.write(',\t\t')
#
#             for joint_str in finger_strs:
#                 fd.write(joint_str)
#                 fd.write(',\t')
#
#             for bgeo_str in bgeo_strs:
#                 fd.write(bgeo_str)
#                 fd.write(',\t')
#
#             fd.write("%8.04f,\t" % confidence)
#             fd.write("%d" % valid)
#
#             fd.write("\n")
#
#         fd.flush()
#         fd.close()
#         self.threadSign = 0
#         message = fn + " has been saved successfully\n"
#         self.message('filesave', message, 0, len(message), 'purple', False, True)
#
#         if (self.file.exists(fn)):
#             self.file.delete(fn)
#             self.file.insert('', 0, text=fn, iid=fn, values=(str(self.maxtimes), str(datetime.datetime.now())[:-7]))
#         else:
#             self.file.insert('', 0, text=fn, iid=fn, values=(str(self.maxtimes), str(datetime.datetime.now())[:-7]))
#
#         # app.plot(self.tip_co, self.joint_series, self.confs, self.N)