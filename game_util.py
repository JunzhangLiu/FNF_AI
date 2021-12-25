from PIL import Image
import win32gui, win32process, win32ui, win32con
from win32com.client import GetObject
import numpy as np
import ctypes
import ctypes.wintypes
import time


def screenshot(args, l=700,t=80,w=440,h=105, arrow_width=105,blank=5,channels=3):
    dc,dc_obj,c_dc = args['dc'],args['dc_obj'],args['c_dc']
    bit_map = win32ui.CreateBitmap()
    bit_map.CreateCompatibleBitmap(dc_obj, w+1, h)
    c_dc.SelectObject(bit_map)
    c_dc.BitBlt((0,0),(w+1, h) , dc_obj, (l,t), win32con.SRCCOPY)    
    bit_map_str = bit_map.GetBitmapBits(True)
    bit_map_info = bit_map.GetInfo()
    img = Image.frombuffer('RGB',(bit_map_info['bmWidth'], bit_map_info['bmHeight']),bit_map_str, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(bit_map.GetHandle())
    if channels==1:
        img = img.convert('L')
    img = np.array(img,dtype=np.uint8)
    arrows = []
    for i in range(4):
        start = (arrow_width+blank+2)*i
        arrows.append(img[:,start:start+arrow_width])
    img = np.expand_dims(np.array(arrows,dtype=np.uint8),axis=-1)
    return img

def wait_for(callback,process,fun = (lambda x,args:x),args=None):
    game_crashed = False
    while not fun(callback(),args):
        success = process.is_responding()
        if not success:
            game_crashed = not process.recovered()
    return game_crashed

def get_win_handle(pid,timeout = 10):
    def enum_window(windle_handle, results,pid):
        win_pid = win32process.GetWindowThreadProcessId(windle_handle)[1]
        if win_pid == pid:
            results.append((windle_handle, win32gui.GetWindowText(windle_handle), win32gui.GetClassName(windle_handle)))
    windows = []
    win32gui.EnumWindows(lambda x,y:enum_window(x,y,pid), windows)
    tries = 0
    while tries<timeout and len(windows)==0:
        print('window not opend, try {:d}/{:d}'.format(tries,timeout),end='\r')
        time.sleep(1)
        win32gui.EnumWindows(lambda x,y:enum_window(x,y,pid), windows)
        tries+=1
    print()
    win = [i for i in windows if i[2] == 'SDL_app']
    return win[0][0]
    
def get_pid(name="Funkin.exe"):
    WMI = GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    pid = None
    for p in processes:
        if (str(p.Properties_("Name").Value) == name):
            pid = p.Properties_("ProcessID").Value
            break
    if pid is None:
        raise Exception('cannot find process')
    return pid

def get_proc_handle(pid):
    # ctypes.windll.kernel32.OpenProcess.argtypes = [ctypes.wintypes.DWORD,ctypes.wintypes.BOOL,ctypes.wintypes.DWORD]
    all_access = 0x1F0FFF
    handle = ctypes.windll.kernel32.OpenProcess(all_access, False, pid)
    # err = ctypes.GetLastError()
    # if err != 0:
    #     raise Exception('Errcode {:d}'.format(err))
    return handle

def get_screenshot_args(hadle):
    dc = win32gui.GetWindowDC(hadle)
    dc_obj=win32ui.CreateDCFromHandle(dc)
    c_dc=dc_obj.CreateCompatibleDC()
    args = {}
    args['handle'] = hadle
    args['dc'] = dc
    args['dc_obj'] = dc_obj
    args['c_dc'] = c_dc
    return args