import subprocess
import os
import time
import pygetwindow
import pyautogui
from PIL import ImageGrab
from PIL import Image,ImageWin
import win32gui, win32ui, win32con, win32process, win32api
import numpy as np



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
            return self.process
        self.terminate()
        self.process = subprocess.Popen([self.path],stdout=self.stdout, stderr=self.stderr,cwd=self.cwd)
        return self.process
    def terminate(self):
        self.process.terminate()
    def get_pid(self):
        if self.process is None:
            return None
        return self.process.pid
        

def screenshot(handle):
    rect = win32gui.GetWindowRect(handle)
    width, height = rect[2] - rect[0], rect[3] - rect[1]
    
    context = win32gui.GetWindowDC(handle)
    device_context=win32ui.CreateDCFromHandle(context)
    compatible_device_context=device_context.CreateCompatibleDC()

    bit_map = win32ui.CreateBitmap()
    bit_map.CreateCompatibleBitmap(device_context, width, height)
    compatible_device_context.SelectObject(bit_map)
    compatible_device_context.BitBlt((0,0),(width, height) , device_context, (0,0), win32con.SRCCOPY)

    bit_map_str = bit_map.GetBitmapBits(True)
    bit_map_info = bit_map.GetInfo()
    img = Image.frombuffer('RGB',(bit_map_info['bmWidth'], bit_map_info['bmHeight']),bit_map_str, 'raw', 'BGRX', 0, 1)
    
    device_context.DeleteDC()
    compatible_device_context.DeleteDC()
    win32gui.ReleaseDC(handle, context)
    win32gui.DeleteObject(bit_map.GetHandle())
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


process = Game_process('D:\\ai\\fnf\\game\\Funkin.exe',"D:\\ai\\fnf\\game",stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.start()
pid = process.get_pid()

time.sleep(3)

handle = get_win_handle(pid)
start = time.time()
img = screenshot(handle)
print(time.time()-start)
img.save("foo.png")
process.terminate()
