import imp
from numpy.lib.function_base import disp
from game_process import Game_process
from mem import *
import time
from model import *
from game_util import *
import random
from model import FNF_Visual
import tensorflow as tf
from tensorflow import keras
from song_itr import Song_iterator
from navigating import *
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

i = 0
data_size = mem.get_data_size()
game_crashed = False

while True:
    screenshot_args=process.restart()
    success = start_game(process,keyboard)
    while not success:
        success = start_game(process,keyboard)
        screenshot_args=process.restart()
        time.sleep(6)
    game_crashed = False

    song_name,number,level,length_in_millisec=iterator.get_next_song_info()
    length_in_sec = length_in_millisec/1000
    print('song name: {:s}, level: {:d}, length: {:f}'.format(song_name,level,length_in_sec))

    success = select_song(number,process,keyboard)
    if not success:
        game_crashed = True
        continue
    success = select_level(level,process,keyboard)
    if not success:
        game_crashed = True
        continue

    mem.start(length_in_sec)
    dead = False
    timer0 = process.get_time()
    game_crashed= wait_for(lambda : timer0-process.get_time()!=0, process)
    game_crashed= wait_for(lambda : process.get_time()>=2000, process)

    timer0 = timer = process.get_time()
    print("game_start")
    while timer<length_in_millisec and not dead and not game_crashed:
        timer = process.get_time()
        # print(timer)
        img = screenshot(screenshot_args, l=l,t=t,w=w,h=h,channels=channels)
        dead = np.average(img) < 3
        
        if timer-timer0<15:
            continue

        mem.store(img,timer/1000)
        action = model(img)
        action = tf.reshape(action,[4]).numpy()
            
        if data_size >= training_start:
            # if action.max() > 0.9:
            #     print(timer,action)
            for idx, a in enumerate(action):
                current_keycode = GAME_KEYS[idx]
                if a > 0.9:
                    keyboard.PressKey(current_keycode)
                    # print('key {:d} pressed by program'.format(idx))
                else:
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






