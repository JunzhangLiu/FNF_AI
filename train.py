import imp
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

save_every = 10
#Crop Param
l=700
t=80
w=440
h=110
lr = 0.1
model = FNF_Visual()
model(np.zeros((1,h,w,3)))
optimizer = keras.optimizers.Adam(learning_rate=lr)
model.compile(optimizer=optimizer,loss=tf.keras.losses.BinaryCrossentropy(),metrics=['accuracy'])
keyboard = Keyboard()


mem = Memory(w,h)
# mem.load()
process = Game_process('D:\\ai\\fnf\\game\\Funkin.exe',"D:\\ai\\fnf\\game",stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# pid,win_handle,proc_handle, base_addr = process.start()
# print('process started successfully, pid is {:d}, win_handle is {:d}, proc_handle is {:d}'.format(pid, win_handle, proc_handle))

# while start_game(process):
#     pid,win_handle,proc_handle, base_addr=process.restart()


# song = song_list[random.randrange(len(song_list))]
song_list = json.load(open("song_list.json"))["list"]
i = 0
data_size = 0
game_crashed = False

ckpt = tf.train.Checkpoint(model)
while True:
    pid,win_handle,proc_handle, base_addr=process.restart()
    while start_game(process):
        pid,win_handle,proc_handle, base_addr=process.restart()
        time.sleep(6)
    game_crashed = False

    song = song_list[0]
    song = song_list[random.randrange(len(song_list)-3)]
    name,number = list(song.items())[0]
    difficulties = song['difficulties']
    difficulty = random.randrange(0,2)


    file_name = difficulties[difficulty]
    print(file_name,difficulty)

    if select_song(number,process):
        game_crashed = True
        continue

    length_in_millisec = song_length(name,file_name)
    length_in_sec = length_in_millisec/1000
    mem.start(name,length_in_sec)

    if select_difficulty(difficulty,process):
        game_crashed = True
        continue


    print("game_start")
    dead = False
    timer0 = timer = process.get_timer()
    while timer0-timer==0 and not game_crashed:
        timer = process.get_timer()
        if not process.is_responding():
            game_crashed = True
        
    while timer<1000 and not game_crashed:
        timer = process.get_timer()
        if not process.is_responding():
            game_crashed = True
    while timer<length_in_millisec and not dead and not game_crashed:
        start = time.time()
        timer = process.get_timer()
        # print(timer)
        img = screenshot(win_handle)
        mem.store(img,timer/1000)
        dead = np.average(img) < 3
        action = model(np.expand_dims(img,axis=0))
        # print(timer,action)
        for idx, a in enumerate(action[0]):
            current_keycode = GAME_KEYS[idx]
            if data_size >= 5000:
                noise = random.randrange(0,1000)
                if noise < 2:
                    if keyboard.pressed(current_keycode):
                        print('random key release {:d}'.format(idx))
                        keyboard.ReleaseKey(current_keycode)
                    else:
                        print('random key presse {:d}'.format(idx))
                        keyboard.PressKey(current_keycode)
                if a > 0.9:
                    keyboard.PressKey(current_keycode)
                    print(timer,action)
                    print('key {:d} pressed by program'.format(idx))
                else:
                    keyboard.ReleaseKey(current_keycode)
        # print(time.time()-start)

    keyboard.release_all_keys()
    print('game over')

    # if not process.is_responding():
    #     game_crashed = True
    #     continue

    # if dead and not game_crashed:
    #     if exit_song(dead,process):
    #         game_crashed = True
    #     time.sleep(6)
    #     if main_menu_to_song_list(process):
    #         game_crashed = True
    if game_crashed:
        continue
    
    mem.end()
    notes = load_notes(name,file_name)
    mem.compute_ground_truth(notes)
    data_size = mem.get_data_size()
    print(data_size)
    if data_size >= 5000:
        x,y = mem.get_data()
        model.fit(x,y,batch_size=128,epochs=min(10,data_size//5000))
    
    if i%save_every == 0:
        print('saving')
        mem.save()
        ckpt.write("./saved_model/model")
    i+=1
    # with_key,y_true,no_key = mem.get_new_data()
    # for i in range(5):
    #     data = np.concatenate([with_key,no_key[np.random.choice(no_key.shape[0],size=with_key.shape[0])]])
    #     y = np.zeros((data.shape[0],4))
    #     y[0:with_key.shape[0]] = y_true
    #     model.fit(data,y,batch_size=data.shape[0],epochs=1)

                

        




