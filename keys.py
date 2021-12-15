import ctypes
import time
# import threading
# import sys
SendInput = ctypes.windll.user32.SendInput

ENTER = 0x1C
UP = 0xC8
LEFT = 0xCB
RIGHT = 0xCD
DOWN = 0xD0
GAME_KEYS = [LEFT,DOWN,UP,RIGHT]

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class Keyboard(object):
    def __init__(self):
        self.pressed_keys = {ENTER:0, UP:0, LEFT:0,RIGHT:0,DOWN:0}
    def PressKey(self,key):
        if self.pressed_keys[key]:
            return
        self.pressed_keys[key] = 1
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput( 0, key, 0x0008, 0, ctypes.pointer(extra) )
        x = Input( ctypes.c_ulong(1), ii_ )
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def hold_key(self, key):
        self.pressed_keys[key] = 1

    def send_input(self):
        for key in GAME_KEYS:
            if self.pressed_keys[key]:
                self.PressKey(key)
    def ReleaseKey(self,key):
        if not self.pressed_keys[key]:
            return
        self.pressed_keys[key] = 0
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput( 0, key, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
        x = Input( ctypes.c_ulong(1), ii_ )
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    def pressed(self,key):
        return self.pressed_keys[key]
    def release_all_keys(self):
        for key in GAME_KEYS:
            if self.pressed_keys[key]:
                self.ReleaseKey(key)

def keyboard_thread_f(queue):
    keyboard = Keyboard()
    while True:
        ud, key = queue.get()
        if ud:
            keyboard.hold_key(key)
        else:
            keyboard.ReleaseKey(key)
        keyboard.send_input()
