import imp
from numpy.lib.function_base import disp
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
from song_itr import Song_iterator
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
channels = 1
model = FNF_Visual()
load = True
ckpt = tf.train.Checkpoint(model)
if load:
    ckpt.read("./saved_model/model")
optimizer = keras.optimizers.Adam(learning_rate=lr)
model.compile(optimizer=optimizer,loss=tf.keras.losses.BinaryCrossentropy(),metrics=['accuracy'])
iterator = Song_iterator()

model(np.zeros((1,arrow_width,h,channels)))
keyboard = Keyboard()


mem = Memory(arrow_width,h,c=channels, load = load)
process = Game_process('D:\\ai\\fnf\\game\\Funkin.exe',"D:\\ai\\fnf\\game")

# song_list = json.load(open("song_list.json"))["list"]
i = 0
data_size = mem.get_data_size()
game_crashed = False

while True:
    pid,win_handle,proc_handle, base_addr,screenshot_args=process.restart()
    success = start_game(process)
    while not success:
        success = start_game(process)
        pid,win_handle,proc_handle, base_addr,screenshot_args=process.restart()
        time.sleep(6)
    game_crashed = False

    # song = song_list[0]
    # song = song_list[random.randrange(len(song_list)-3)]
    # # song = song_list[4]
    # name,number = list(song.items())[0]
    # difficulties = song['difficulties']
    # difficulty = random.randrange(0,2)


    # file_name = difficulties[difficulty]
    # length_in_millisec = song_length(name,file_name)

    song_name,number,level,length_in_millisec=iterator.get_next_song_info()
    length_in_sec = length_in_millisec/1000
    print('song name: {:s}, level: {:d}, length: {:f}'.format(song_name,level,length_in_sec))
    success = select_song(number,process)

    if not success:
        game_crashed = True
        continue

    mem.start(length_in_sec)

    success = select_level(level,process)
    if not success:
        game_crashed = True
        continue

    print("game_start")
    dead = False
    timer0 = process.get_time()

    game_crashed=while_wait(lambda timer: timer0-timer==0, lambda : process.get_time(), process)

    game_crashed=while_wait(lambda timer: timer<2000, lambda : process.get_time(), process)

    j = 0
    display = 50
    timer0 = timer = process.get_time()
    while timer<length_in_millisec and not dead and not game_crashed:
        timer = process.get_time()
        # print(timer)
        img = screenshot(screenshot_args, l=l,t=t,w=w,h=h,channels=channels)
        dead = np.average(img) < 3
        
        if timer-timer0<15:
            continue

        mem.store(img,timer/1000)
        action = model(img)
        
        for idx, a in enumerate(action):
            current_keycode = GAME_KEYS[idx]
            noise = random.randrange(0,10000)
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
        timer0=timer
    keyboard.release_all_keys()
    print('game over')

    if game_crashed:
        continue

    mem.end()
    notes = iterator.get_sections()
    mem.compute_ground_truth(notes)
    data_size = mem.get_data_size()
    print(data_size)
    if data_size >= training_start:
        x,y = mem.get_data()
        model.fit(x,y,batch_size=128,epochs=min(5,data_size//10000))
    print(i)
    if i%save_frequency == 0:
        print('saving')
        mem.save()
        ckpt.write("./saved_model/model")
    i+=1






