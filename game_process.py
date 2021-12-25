import subprocess
import win32gui, win32process, win32ui, win32con, win32api
import ctypes
import ctypes.wintypes
import time
class Game_process(object):
    def __init__(self,path,cwd,stdin=None,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        self.path = path
        self.cwd = cwd
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.process = None
        self.type_to_ctype = {'d':(ctypes.c_double,ctypes.c_ulonglong),'int':(ctypes.c_int,ctypes.c_ulonglong)}
        
    def start(self):
        if self.process is None:
            self.process = subprocess.Popen([self.path],stdin = self.stdin, stdout=self.stdout, stderr=self.stderr,cwd=self.cwd)
        else:
            self.terminate()
            self.process = subprocess.Popen([self.path],stdin = self.stdin, stdout=self.stdout, stderr=self.stderr,cwd=self.cwd)
        self.pid = self.process.pid

        self.win_handle = self.get_win_handle()
        
        all_access = 0x1F0FFF
        self.proc_handle = ctypes.windll.kernel32.OpenProcess(all_access, False, self.pid)

        modules = win32process.EnumProcessModules(self.proc_handle)
        self.base = modules[0]  
        dc = self.get_screenshot_args()
        return dc
    def terminate(self):
        if self.process is not None:
            self.process.terminate()

    def get_pid(self):
        if self.process is None:
            return None
        return self.process.pid

    def is_responding(self):
        cmd = 'tasklist /FI "PID eq %d" /FI "STATUS eq running"' % self.pid
        status = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
        return str(self.pid) in str(status)

    def restart(self):
        self.terminate()
        return self.start()

    def get_win_handle(self,timeout = 10):
        def enum_window(windle_handle, results,pid):
            win_pid = win32process.GetWindowThreadProcessId(windle_handle)[1]
            if win_pid == pid:
                results.append((windle_handle, win32gui.GetWindowText(windle_handle), win32gui.GetClassName(windle_handle)))
        windows = []
        win32gui.EnumWindows(lambda x,y:enum_window(x,y,self.pid), windows)
        win = [i for i in windows if i[2] == 'SDL_app']
        tries = 0
        while tries<timeout and len(win)==0:
            print('window not opend, try {:d}/{:d}'.format(tries,timeout),end='\r')
            time.sleep(1)
            win32gui.EnumWindows(lambda x,y:enum_window(x,y,self.pid), windows)
            win = [i for i in windows if i[2] == 'SDL_app']
            tries += 1
        if len(windows)==0:
            raise Exception('failed to find window')
        
        return win[0][0]

    def get_time(self):
        timer_addr = 0xCC8748
        return self.get_addr_val(timer_addr,t='d')
    def get_status(self):
        status_addr = 0xCCCF30
        return self.get_addr_val(status_addr,t='int')


    def get_addr_val(self,addr, t = 'd'):
        addr = self.base + addr
        types,byte = self.type_to_ctype[t]
        buffer = types()
        bytes_read = byte()
        ctypes.windll.kernel32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE,ctypes.wintypes.LPCVOID,ctypes.wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
        ctypes.windll.kernel32.ReadProcessMemory(self.proc_handle, addr, ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytes_read))
        # timer = struct.unpack(t, buffer)
        return buffer.value
    
    def menu_key(self,keyboard, key):
        crashed = False
        if not self.is_responding():
            crashed = not self.recovered()
        if crashed:
            return crashed

        keyboard.PressKey(key)
        time.sleep(0.5)
        keyboard.ReleaseKey(key)

        if not self.is_responding():
            crashed = not self.recovered()
        return crashed
    
    def recovered(self,time_out = 10, wait = 5):
        for i in range(time_out):
            time.sleep(wait)
            if self.is_responding():
                return True
        return False

    def wait_check(self,time_sleep):
        if not self.is_responding():
            return False
        time.sleep(time_sleep)
        if not self.is_responding():
            return False
        return True

    def get_screenshot_args(self):
        dc = win32gui.GetWindowDC(self.win_handle)
        dc_obj=win32ui.CreateDCFromHandle(dc)
        c_dc=dc_obj.CreateCompatibleDC()
        args = {}
        args['handle'] = self.win_handle
        args['dc'] = dc
        args['dc_obj'] = dc_obj
        args['c_dc'] = c_dc
        return args
        

        
