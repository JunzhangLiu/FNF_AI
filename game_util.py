import subprocess
import time
from PIL import ImageGrab,Image
import win32gui, win32process, win32ui, win32con, win32api
from win32com.client import GetObject
import numpy as np
from keys import *
import json
import struct
import ctypes
import ctypes.wintypes

keyboard = Keyboard()
class Game_process(object):
    def __init__(self,path,cwd,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        self.path = path
        self.cwd = cwd
        self.stdout = stdout
        self.stderr = stderr
        self.process = None
    def start(self):
        if self.process is None:
            self.process = subprocess.Popen([self.path],stdout=self.stdout, stderr=self.stderr,cwd=self.cwd)
        else:
            self.terminate()
            self.process = subprocess.Popen([self.path],stdout=self.stdout, stderr=self.stderr,cwd=self.cwd)
        time.sleep(10)
        self.pid = get_pid()
        self.win_handle = get_win_handle(self.pid)
        self.proc_handle = get_proc_handle(self.pid)
        self.base = get_base_addr(self.proc_handle)
        return self.pid, self.win_handle, self.proc_handle, self.base
    def terminate(self):
        if self.process is not None:
            self.process.terminate()
    def get_pid(self):
        if self.process is None:
            return None
        return self.process.pid
    def get_timer(self):
        self.proc_handle = get_proc_handle(self.pid)
        self.base = get_base_addr(self.proc_handle)
        return get_time(self.proc_handle,self.base)
    def is_responding(self):
        cmd = 'tasklist /FI "PID eq %d" /FI "STATUS eq running"' % self.pid
        status = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
        return str(self.pid) in str(status)
    def restart(self):
        self.terminate()
        return self.start()

def screenshot(handle,l=700,t=80,w=440,h=110):
    rect = win32gui.GetWindowRect(handle)
    # width, height = rect[2] - rect[0], rect[3] - rect[1]
    # l = 700
    # t = 50
    # w = h = 440
    x = rect[0] + l
    y = rect[1] + t
    img = ImageGrab.grab((x, y, x+w, y+h))
    img = np.array(img,dtype=np.uint8)
    # context = win32gui.GetWindowDC(handle)
    # device_context=win32ui.CreateDCFromHandle(context)
    # compatible_device_context=device_context.CreateCompatibleDC()

    # bit_map = win32ui.CreateBitmap()
    # bit_map.CreateCompatibleBitmap(device_context, width, height)
    # compatible_device_context.SelectObject(bit_map)
    # compatible_device_context.BitBlt((0,0),(width, height) , device_context, (0,0), win32con.SRCCOPY)

    # bit_map_str = bit_map.GetBitmapBits(True)
    # bit_map_info = bit_map.GetInfo()
    # img = Image.frombuffer('RGB',(bit_map_info['bmWidth'], bit_map_info['bmHeight']),bit_map_str, 'raw', 'BGRX', 0, 1)
    
    # device_context.DeleteDC()
    # compatible_device_context.DeleteDC()
    # win32gui.ReleaseDC(handle, context)
    # win32gui.DeleteObject(bit_map.GetHandle())
    return img

def get_win_handle(pid):
    def _windowEnumerationHandler(windle_handle, results,pid):
        win_pid = win32process.GetWindowThreadProcessId(windle_handle)[1]
        if win_pid == pid:
            results.append((windle_handle, win32gui.GetWindowText(windle_handle), win32gui.GetClassName(windle_handle)))
    windows = []
    win32gui.EnumWindows(lambda x,y:_windowEnumerationHandler(x,y,pid), windows)
    win = [i for i in windows if i[2] == 'SDL_app']
    return win[0][0]

def crop_img(img):
    l = 700
    t = 50
    w = h = 440
    return img.crop((l,t,l + w, t + h))
   
def start_game(process):
    time.sleep(7)
    print("start_game")
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True

    time.sleep(2)


    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True
    time.sleep(7)

    return main_menu_to_song_list(process)
    

def select_song(number,process):
    for i in range(number):
        keyboard.PressKey(DOWN)
        time.sleep(0.5)
        keyboard.ReleaseKey(DOWN)
        if not process.is_responding():
            return True
        time.sleep(3)
    return False


def select_difficulty(difficulty,process):
    #impliment difficulty selection
    for i in range(difficulty):
        keyboard.PressKey(RIGHT)
        time.sleep(0.5)
        keyboard.ReleaseKey(RIGHT)      
        if not process.is_responding():
            return True

        time.sleep(3)

    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True

    return False
    
def exit_song(dead,process):
    if dead:
        time.sleep(5)
        keyboard.PressKey(ENTER)
        time.sleep(0.5)
        keyboard.ReleaseKey(ENTER)     
        if not process.is_responding():
            return True

        time.sleep(10)
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True

    time.sleep(1)
    keyboard.PressKey(DOWN)
    time.sleep(0.5)
    keyboard.ReleaseKey(DOWN)
    if not process.is_responding():
        return True
        
    time.sleep(1)
    keyboard.PressKey(DOWN)
    time.sleep(0.5)
    keyboard.ReleaseKey(DOWN)
    if not process.is_responding():
        return True

    time.sleep(1)
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True
        
    return False

def main_menu_to_song_list(process):
    keyboard.PressKey(DOWN)
    time.sleep(0.5)
    keyboard.ReleaseKey(DOWN)
    if not process.is_responding():
        return True

    time.sleep(1)
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return True

    time.sleep(10)
    return False


def load_notes(song,difficulty):
    #impliment difficulty selection
    # notes = json.load(open("./game/assets/data/"+song+"/"+difficulty+".json"))['song']['notes']
    # return notes
    file_path = "./game/assets/data/"+song+"/"+difficulty+".json"
    try:
        notes = json.load(open(file_path))['song']['notes']
        print('success')
    except Exception as e:
        e_str = str(e)
        if 'Extra data' in e_str:
            line_num = int(e_str[e_str.find('line ')+5:e_str.find(' column')])
            col_num = int(e_str[e_str.find('column ')+7:e_str.find(' (')])
            char = int(e_str[e_str.find('char ')+5:len(e_str)-1])
            # print(e_str,line_num,col_num,char)
            file = open(file_path)
            file_data = ''
            for i in range(line_num-1):
                file_data+=file.readline()
            file_data+=file.readline()[:col_num-1]
            file.close()
            notes = json.loads(file_data)['song']['notes']
            print(file_path,'success')
        else:
            raise Exception('Never seen this one')
    return notes
def song_length(song,difficulty):
    #impliment difficulty selection
    sections = load_notes(song,difficulty)
    for section in reversed(sections):
        if section['mustHitSection']:
            section_notes = section['sectionNotes']
            if len(section_notes)>0:
                last_note = section_notes[-1]
                return last_note[0]+last_note[2]
    return -1


def get_pid(name="Funkin.exe"):
    WMI = GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    for p in processes:
        if (str(p.Properties_("Name").Value) == name):
            pid = p.Properties_("ProcessID").Value
            break
    return pid

def get_proc_handle(pid):
    # ctypes.windll.kernel32.OpenProcess.argtypes = [ctypes.wintypes.DWORD,ctypes.wintypes.BOOL,ctypes.wintypes.DWORD]
    all_access = 0x1F0FFF
    handle = ctypes.windll.kernel32.OpenProcess(all_access, False, pid)
    # err = ctypes.GetLastError()
    # if err != 0:
    #     raise Exception('Errcode {:d}'.format(err))
    return handle

def get_base_addr(handle):
    modules = win32process.EnumProcessModules(handle)
    base_addr = modules[0]  
    # err = ctypes.GetLastError()
    # if err != 0:
    #     raise Exception('Errcode {:d}'.format(err))
    return base_addr

def get_time(handle, base_addr):
    timer_addr = 0xCC8748
    addr = base_addr + timer_addr
    buffer = ctypes.c_double()
    bytesRead = ctypes.c_ulonglong()
    ctypes.windll.kernel32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE,ctypes.wintypes.LPCVOID,ctypes.wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
    ctypes.windll.kernel32.ReadProcessMemory(handle, addr, ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytesRead))
    timer = struct.unpack('d', buffer)
    # err = ctypes.GetLastError()
    # if err != 0:
    #     raise Exception('Errcode {:d}'.format(err))
    return buffer.value



# process = Game_process('D:\\ai\\fnf\\game\\Funkin.exe',"D:\\ai\\fnf\\game",stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# process.start()
# pid = get_pid()
# handle = get_proc_handle(pid)
# base = get_base_addr(handle)
# start = time.time()
# print(get_time(handle,base))
# print(time.time() - start)


# # def get_time(pid):
# #     handle = ctypes.windll.kernel32.OpenProcess(0xFFFF, False, pid)
#     err = ctypes.GetLastError()
#     if err != 0:
#         print(err)
#         raise Exception
#     addr = 0x7FF6224E8748
#     buffer = ctypes.c_double()
#     bytesRead = ctypes.c_ulonglong()
#     ctypes.windll.kernel32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE,ctypes.wintypes.LPCVOID,ctypes.wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
#     ctypes.windll.kernel32.ReadProcessMemory(handle, addr, ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(bytesRead))
#     timer = struct.unpack('d', buffer)
#     err = ctypes.GetLastError()
#     if err != 0:
#         print(err)
#         raise Exception
#     return timer[0]




# pid = get_pid()
# print(pid)
# print(get_time(pid))


# # start_game()
# time.sleep(5)

# handle = get_win_handle(pid)
# start = time.time()
# img = screenshot(handle)
# Image.fromarray(img).show()
# print(time.time()-start)
# img.save("foo.png")
# process.terminate()
