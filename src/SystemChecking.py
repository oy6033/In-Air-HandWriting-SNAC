import os, sys, inspect

class Application(object):

    def __init__(self):
        self.separator = ''
        self.single = ''
        self.video_encoding = ''
    def system_checking(self):
        src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
        if 'linux' in str(sys.platform):
            arch_dir = '../lib_Linux/x64' if sys.maxsize > 2 ** 32 else '../lib_Linux/x86'
            self.separator = '../'
            self.single = '/'
            self.video_encoding = '.avi'
        elif 'win32' in str(sys.platform):
            arch_dir = '../lib_Windows/x64' if sys.maxsize > 2 ** 32 else '../lib_Windows/x86'
            self.separator = '..\\'
            self.single = '\\'
            self.video_encoding = '.mp4'
        elif 'darwin' in str(sys.platform):
            arch_dir = '../lib_Mac' if sys.maxsize > 2 ** 32 else '../lib_Mac'
            self.separator = '../'
            self.single = '/'
            self.video_encoding = '.avi'
        else:
            sys.exit()
        sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

        return src_dir, arch_dir

    def create_file(self):
        if not os.path.exists(self.separator+'leap_data'):
            os.makedirs(self.separator+'leap_data')
        if not os.path.exists(self.separator+'video'):
            os.makedirs(self.separator+'video')
        if not os.path.exists(self.separator+'glove_data'):
            os.makedirs(self.separator+'glove_data')
