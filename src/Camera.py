import threading
import cv2
from PIL import ImageTk
import PIL.Image
import datetime
import SystemChecking
check = SystemChecking.Application()
src_dir, arch_dir = check.system_checking()
class Camera(threading.Thread):
    def __init__(self, fn, maxtimes, l, t, file, message):
        threading.Thread.__init__(self)
        self.fn = fn
        self.maxtimes = maxtimes
        self.stop = 0
        self.l = l
        self.t = t
        self.file = file
        self.message = message


    def run(self):
        cap = cv2.VideoCapture(0)
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(check.separator+'video'+check.single + self.fn, fourcc, 20, (640, 480))

        while cap.isOpened():
            ret, frame = cap.read()
            if ret == True:
                frame = cv2.flip(frame, 90)
                # write the flipped frame
                out.write(frame)
                # cv2.imshow('In-Air hand Writing Recorder', frame)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = PIL.Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.l.imgtk = imgtk
                self.l.configure(image=imgtk)
                if self.stop == 1:
                    break
            else:
                break
        # Release everything if job is finished
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        time = str(datetime.datetime.now())[:-7]
        if (self.file.exists(self.fn)):
            self.file.delete(self.fn)
            self.file.insert('', 0, text=self.fn, iid=self.fn, values=(str(self.maxtimes), time))
        else:
            self.file.insert('', 0, text=self.fn, iid=self.fn, values=(str(self.maxtimes), time))

        message = self.fn + " has been saved successfully\n"
        self.message('videosave', message, 0, len(message), 'purple', False, True)