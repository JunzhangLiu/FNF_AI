import imp
from game_process import Game_process
# from get_time import get_time
from mem import *
import time
import json
from model import *
from game_util import *
import random
from model import FNF_Visual
import tensorflow as tf
from tensorflow import keras
import win32gui, win32process, win32ui, win32con, win32api
import struct
import ctypes
import ctypes.wintypes

save_frequency = 10
training_start = 10000
#Crop Param
l=700
t=80
w=450
h=105
lr = 0.1
arrow_width = 105
blank = 5

model = FNF_Visual()
load = True
ckpt = tf.train.Checkpoint(model)
if load:
    ckpt.read("./saved_model/model")
optimizer = keras.optimizers.Adam(learning_rate=lr)
model.compile(optimizer=optimizer,loss=tf.keras.losses.BinaryCrossentropy(),metrics=['accuracy'])

model(np.zeros((1,arrow_width,h,3)))
keyboard = Keyboard()


mem = Memory(arrow_width,h, load = load)
process = Game_process('D:\\ai\\fnf\\game\\Funkin.exe',"D:\\ai\\fnf\\game",stdout=subprocess.PIPE, stderr=subprocess.PIPE)

song_list = json.load(open("song_list.json"))["list"]
i = 0
data_size = mem.get_data_size()
game_crashed = False

while True:
    pid,win_handle,proc_handle, base_addr=process.restart()
    success = start_game(process)
    while not success:
        success = start_game(process)
        pid,win_handle,proc_handle, base_addr=process.restart()
        time.sleep(6)
    game_crashed = False

    # song = song_list[0]
    song = song_list[random.randrange(len(song_list)-3)]
    # song = song_list[0]
    name,number = list(song.items())[0]
    difficulties = song['difficulties']
    difficulty = random.randrange(0,2)


    file_name = difficulties[difficulty]
    length_in_millisec = song_length(name,file_name)
    length_in_sec = length_in_millisec/1000
    print(file_name,difficulty)
    success = select_song(number,process)
    if not success:
        game_crashed = True
        continue

    mem.start(name,length_in_sec)

    success = select_difficulty(difficulty,process)
    if not success:
        game_crashed = True
        continue


    print("game_start")
    dead = False
    timer0 = timer = process.get_time()
    while timer0-timer==0 and not game_crashed:
        timer = process.get_time()
        success = process.is_responding()
        if not success:
            game_crashed = True

    while timer<1000 and not game_crashed:
        timer = process.get_time()
        success = process.is_responding()
        if not success:
            game_crashed = True
    while timer<length_in_millisec and not dead and not game_crashed:
        start = time.time()
        timer = process.get_time()
        # print(timer)
        img = screenshot(win_handle, l=l,t=t,w=w,h=h)
        mem.store(img,timer/1000)
        dead = np.average(img) < 3
        action = model(img)
        # print(timer,action)
        for idx, a in enumerate(action):
            current_keycode = GAME_KEYS[idx]
            noise = random.randrange(0,1000)
            if noise < 2:
                if keyboard.pressed(current_keycode):
                    print('random key release {:d}'.format(idx))
                    keyboard.ReleaseKey(current_keycode)
                else:
                    print('random key presse {:d}'.format(idx))
                    keyboard.PressKey(current_keycode)
            elif data_size >= training_start:
                if a[0] > 0.9:
                    keyboard.PressKey(current_keycode)
                    print(timer,action)
                    print('key {:d} pressed by program'.format(idx))
                else:
                    keyboard.ReleaseKey(current_keycode)
            elif keyboard.pressed(current_keycode):
                    print('key release {:d}'.format(idx))
                    keyboard.ReleaseKey(current_keycode)

        # print(time.time()-start)

    keyboard.release_all_keys()
    print('game over')

    if game_crashed:
        continue

    mem.end()
    notes = load_notes(name,file_name)
    mem.compute_ground_truth(notes)
    data_size = mem.get_data_size()
    print(data_size)
    if data_size >= training_start:
        x,y = mem.get_data()
        model.fit(x,y,batch_size=128,epochs=min(10,data_size//10000))
    print(i)
    if i%save_frequency == 0:
        print('saving')
        mem.save()
        ckpt.write("./saved_model/model")
    i+=1






