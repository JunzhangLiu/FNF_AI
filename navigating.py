from game_util import wait_for
from keys import *

def press_when(callback,key,process,keyboard,fun = (lambda x,args:x), args=None):
    wait_for(callback,process,fun=fun,args=args)
    return process.menu_key(keyboard,key)

def start_game(process,keyboard):
    print("start_game")
    crashed = press_when((lambda: process.get_status() != 0),ENTER,process,keyboard)
    if crashed:
        return False
    crashed = press_when((lambda: process.get_status() == 4),ENTER,process,keyboard)
    if crashed:
        return False
    return main_menu_to_song_list(process,keyboard)
    

def select_song(number,process,keyboard):
    for i in range(number):
        if not process.is_responding():
            return False
        crashed = process.menu_key(keyboard,DOWN)
        if crashed:
            return False
        time.sleep(3)
    return True

def select_level(level,process,keyboard):
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

    
def main_menu_to_song_list(process,keyboard):
    def inc(x,args):
        if x==args[1]:
            args[0]+=1
        else:
            args[0]=0
        return args
    crashed = process.menu_key(keyboard,DOWN)
    if crashed:
        return False
    time.sleep(1)
    
    crashed = press_when(process.get_status,DOWN,process,keyboard,fun=(lambda x,args: inc(x,args)[0]>10), args=[0,3])
    if crashed:
        return False
    time.sleep(1)
    crashed = process.menu_key(keyboard,ENTER)
    if crashed:
        return False
    wait_for(process.get_status,process,fun=(lambda x,args: inc(x,args)[0]>10), args=[0,5])
    return True
