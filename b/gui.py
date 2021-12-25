from PyQt5 import QtWidgets as qw
# from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication as qa
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QIcon, QPixmap,QImage
from model import FNF_Visual
import tensorflow as tf
import numpy as np
from game_util import *
from keys import *
import sys
import threading
from win32api import GetSystemMetrics
from queue import Queue


app = qa(sys.argv)
class GUI(QMainWindow):
    def __init__(self,screenshot_args,model,keyboard,x,y,wid=500,ht=300,sl=700,st=80,sw=450,sh=105,channels = 1):
        super(GUI,self).__init__()
        self.setGeometry(x,y,wid,ht)
        self.model = model
        self.running = False
        self.sl,self.st,self.sw,self.sh = sl,st,sw,sh
        self.keyboard = keyboard
        self.screenshot_args = screenshot_args
        self.channels = channels
        self.img_scale = 1/2
        self.model_thread = threading.Thread(target=self.run_ai)
        self.init_ui()
        
    def init_ui(self):
        self.init_button()
        self.get_labels()
        self.get_text()
        self.set_pix_map(np.zeros((4,105,105,1)))
        self.set_text([0,0,0,0])
        self.show()
    def init_button(self):
        self.run = qw.QPushButton('start', self)
        self.run.move(10,140)
        self.run.clicked.connect(self.model_thread.start)

        self.stop = qw.QPushButton('end', self)
        self.stop.move(10,180)
        self.stop.clicked.connect(self.stop_ai)
    
    def get_labels(self,width=105,height=105):
        self.labels=[]
        for i in range(4):
            self.labels.append(qw.QLabel(self))
            self.labels[-1].move(i*(width*self.img_scale),10)
            self.labels[-1].resize(width*self.img_scale,height*self.img_scale)
    def get_text(self,width = 105):
        self.text_arr = []
        self.key_arr = []
        self.p=[]
        for i in range(4):
            # x = qw.QLabel(self)
            self.text_arr.append(qw.QLabel(self))
            self.text_arr[i].move(i*width*self.img_scale,80)
            self.key_arr.append(qw.QLabel(self))
            self.key_arr[i].move(i*width*self.img_scale,90)
            self.key_arr[i].setText('release')
            self.p.append(0)

    def set_pix_map(self,arr):
        arr = np.squeeze(arr,axis=-1)
        for i in range(4):
            img = Image.fromarray(arr[i])
            img = img.convert("RGBA")
            img = img.resize((int(img.size[0]*self.img_scale),int(img.size[1]*self.img_scale)),Image.NEAREST)
            img = ImageQt(img)
            pixmap = QPixmap.fromImage(img)
            self.labels[i].setPixmap(pixmap)
            app.processEvents()
    def set_text(self,action):
        for i in range(4):
            self.text_arr[i].setText(str(round(action[i],2)))
            app.processEvents()
            if action[i]>0.9:
                if self.p[i]==0:
                    self.p[i]=1
                    self.key_arr[i].setText('press')
                    app.processEvents()
            else:
                if self.p[i]==1:
                    self.p[i]=0
                    self.key_arr[i].setText('release')
                    app.processEvents()

    def run_ai(self):
        print("started")
        if self.running:
            print('already running')
            return
        self.running = True
        step = 0
        update_display=1
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
            if step%update_display==0:
                self.set_pix_map(img)
                self.set_text(action)
                app.processEvents()
            step+=1
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
try:
    pid = get_pid()
    handle = get_win_handle(pid)
    args = get_screenshot_args(handle)
except Exception as e:
    print('cannot find game process, start new game')
    from game_process import *
    p = Game_process('D:/ai/fnf/game/Funkin.exe',cwd='D:/ai/fnf/game')
    args = p.start()
    handle = args['handle']
    time.sleep(2)
model = FNF_Visual()
load = True
ckpt = tf.train.Checkpoint(model)
if load:
    ckpt.read("./saved_model/model")
print(model(np.zeros((4,105,105,1))))
keyboard = Keyboard()
wid = 300
ht = 300
rect = win32gui.GetWindowRect(handle)
print(rect)
gui = GUI(args,model,keyboard,min(GetSystemMetrics(0)-wid*3,rect[2]),max(GetSystemMetrics(1)-ht*3,rect[1]),wid=wid,ht=300)
sys.exit(app.exec_())

