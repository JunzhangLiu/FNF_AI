from PyQt5 import QtWidgets as qw
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication as qa
from PyQt5.QtGui import QIcon, QPixmap,QImage
from model import FNF_Visual
import tensorflow as tf
import numpy as np
from game_util import *
from keys import *
import random
import sys
import threading
from win32api import GetSystemMetrics



class GUI(QMainWindow):
    def __init__(self,screenshot_args,model,keyboard,x,y,wid=50,ht=300,sl=700,st=80,sw=450,sh=105,channels = 1):
        super(GUI,self).__init__()
        self.setGeometry(x,y,wid,ht)
        self.model = model
        self.running = False
        self.sl,self.st,self.sw,self.sh = sl,st,sw,sh
        self.keyboard = keyboard
        self.screenshot_args = screenshot_args
        self.channels = channels
        self.model_thread = threading.Thread(target=self.run_ai)
        self.init_ui()
        
    def init_ui(self):
        self.init_button()
        self.show()
    def init_button(self):
        self.run = qw.QPushButton('start', self)
        self.run.move(10,140)
        self.run.clicked.connect(self.model_thread.start)

        self.stop = qw.QPushButton('end', self)
        self.stop.move(10,180)
        self.stop.clicked.connect(self.stop_ai)
    def run_ai(self):
        print("started")
        self.running = True
        while self.running:
            img = screenshot(self.screenshot_args, l=self.sl,t=self.st,w=self.sw,h=self.sh,channels=self.channels)
            action = tf.reshape(self.model(img),[4]).numpy()
            if tf.reduce_max(action)>0.9:
                print('y =',tf.reshape(action,[4]),end=" ")
            for idx, a in enumerate(action):
                current_keycode = GAME_KEYS[idx]
                if a > 0.9:
                    self.keyboard.PressKey(current_keycode)
                    print('key {:d} pressed'.format(idx))
                else:
                    self.keyboard.ReleaseKey(current_keycode)
    
    def stop_ai(self):
        if not self.running:
            print('thread not started')
        else:        
            self.running = False
            self.model_thread.join()
            self.keyboard.release_all_keys()
            self.model_thread = threading.Thread(target=self.run_ai)
            self.run.clicked.connect(self.model_thread.start)
            print("stopped")
pid = get_pid()
handle = get_win_handle(pid)
args = get_screenshot_args(handle)
model = FNF_Visual()
load = True
ckpt = tf.train.Checkpoint(model)
if load:
    ckpt.read("./saved_model/model")
print(model(np.zeros((4,105,105,1))))
keyboard = Keyboard()
wid = 50
ht = 300
app = qa(sys.argv)
rect = win32gui.GetWindowRect(handle)
print(rect)
gui = GUI(args,model,keyboard,min(GetSystemMetrics(0)-wid*3,rect[2]),min(GetSystemMetrics(1)-ht*3,rect[1]),wid=50,ht=300)
sys.exit(app.exec_())

