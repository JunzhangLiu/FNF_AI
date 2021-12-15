import time
from PIL import ImageGrab,Image
import win32gui, win32process, win32ui, win32con, win32api
from win32com.client import GetObject
import numpy as np
from keys import *
import json
import ctypes
import ctypes.wintypes

keyboard = Keyboard()

def screenshot(args, l=700,t=80,w=440,h=105, arrow_width=105,blank=5,channels=3):
    # rect = win32gui.GetWindowRect(handle)
    # width, height = rect[2] - rect[0], rect[3] - rect[1]
    # l = 700
    # t = 50
    # w = h = 440
    # x = rect[0] + l
    # y = rect[1] + t
    # dc = win32gui.GetWindowDC(handle)
    # dc_obj=win32ui.CreateDCFromHandle(dc)
    # c_dc=dc_obj.CreateCompatibleDC()
    dc,dc_obj,c_dc = args['dc'],args['dc_obj'],args['c_dc']
    # dc,dc_obj,c_dc = context
    bit_map = win32ui.CreateBitmap()
    bit_map.CreateCompatibleBitmap(dc_obj, w+1, h)
    c_dc.SelectObject(bit_map)
    c_dc.BitBlt((0,0),(w+1, h) , dc_obj, (l,t), win32con.SRCCOPY)
    # dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)

    
    bit_map_str = bit_map.GetBitmapBits(True)
    bit_map_info = bit_map.GetInfo()
    img = Image.frombuffer('RGB',(bit_map_info['bmWidth'], bit_map_info['bmHeight']),bit_map_str, 'raw', 'BGRX', 0, 1)
    
    # img.show()
    # Free Resources
    # dc_obj.DeleteDC()
    # c_dc.DeleteDC()
    # win32gui.ReleaseDC(handle, dc)
    win32gui.DeleteObject(bit_map.GetHandle())
    # return img    
    # img = ImageGrab.grab((x, y, x+w, y+h))
    if channels==1:
        img = img.convert('L')
    img = np.array(img,dtype=np.uint8)
    arrows = []
    for i in range(4):
        start = (arrow_width+blank+2)*i
        arrows.append(img[:,start:start+arrow_width])
    img = np.expand_dims(np.array(arrows,dtype=np.uint8),axis=-1)
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
    if not process.is_responding():
        return False
    time.sleep(7)
    if not process.is_responding():
        return False

    print("start_game")
    crashed = process.menu_key(keyboard,ENTER)
    if crashed:
        return False
    time.sleep(2)
    crashed = process.menu_key(keyboard,ENTER)
    if crashed:
        return False

    time.sleep(7)

    return main_menu_to_song_list(process)
    

def select_song(number,process):
    for i in range(number):
        if not process.is_responding():
            return False
        crashed = process.menu_key(keyboard,DOWN)
        if crashed:
            return False

        time.sleep(3)
    return True

def while_wait(boolean, expression,process):
    game_crashed = False
    while boolean(expression()):
        # timer = process.get_time()
        success = process.is_responding()
        if not success:
            game_crashed = not process.recovered()
    return game_crashed

def select_level(level,process):
    #impliment difficulty selection
    for i in range(level):
        if not process.is_responding():
            return False
            
        crashed = process.menu_key(keyboard,RIGHT)
        if crashed:
            return False
        time.sleep(3)
    crashed = process.menu_key(keyboard,ENTER)
    if crashed:
        return False
    return True
    
def exit_song(dead,process):
    if dead:
        time.sleep(5)
        keyboard.PressKey(ENTER)
        time.sleep(0.5)
        keyboard.ReleaseKey(ENTER)     
        if not process.is_responding():
            return False

        time.sleep(10)
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return False

    time.sleep(1)
    keyboard.PressKey(DOWN)
    time.sleep(0.5)
    keyboard.ReleaseKey(DOWN)
    if not process.is_responding():
        return False
        
    time.sleep(1)
    keyboard.PressKey(DOWN)
    time.sleep(0.5)
    keyboard.ReleaseKey(DOWN)
    if not process.is_responding():
        return False

    time.sleep(1)
    keyboard.PressKey(ENTER)
    time.sleep(0.5)
    keyboard.ReleaseKey(ENTER)
    if not process.is_responding():
        return False
        
    return True

def main_menu_to_song_list(process):
    
    crashed = process.menu_key(keyboard,DOWN)
    if crashed:
        return False
    time.sleep(1)
    
    crashed = process.menu_key(keyboard,ENTER)
    if crashed:
        return False

    time.sleep(10)
    return True


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