import numpy as np
import os
from PIL import Image
class Memory(object):
    def __init__(self,w,h,c=3,arrow_width = 105, blank = 5, img_per_sec=50,load = False):
        super(Memory,self).__init__()
        self.memory = None
        self.w = h
        self.h = w
        self.c = c
        self.arrow_width = arrow_width
        self.blank = blank
        self.expanded = 0
        self.counter = 0
        self.length = -1
        self.img_per_sec = img_per_sec

        self.training_data_counter = 0
        self.capacity = 50000*4
        self.base = 10
        if load:
            self.load()
            self.capacity = self.training_data[0].shape[0]
        else:
            print("do not load")
            self.training_data = (np.zeros((self.capacity,self.h,self.arrow_width,self.c),dtype=np.uint8),np.zeros((self.capacity,),dtype=np.bool))


    def start(self,length):
        self.expanded = 0
        length = 2*length*self.img_per_sec
        self.length = int(length)
        self.memory = ([np.zeros((self.length,4,self.w,self.h,self.c),dtype=np.uint8)],
                        [np.zeros(self.length,dtype=np.float64)])
        self.counter = 0
    def expand(self):
        self.expanded += 1
        print("expanded {:d}, current img_per_sec is {:d}, consider increasing it".format(self.expanded,self.img_per_sec))
        self.memory[0].append(np.zeros((self.length,4,self.w,self.h,self.c),dtype=np.uint8))
        self.memory[1].append(np.zeros(self.length,dtype=np.float64))
    def store(self,img,time):
        if self.counter>=self.length:
            self.expand()
            self.counter = 0
        self.memory[0][-1][self.counter] = img
        self.memory[1][-1][self.counter] = time
        self.counter+=1
    def end(self):
        self.counter-=1
        if self.counter>0:
            self.memory[0][-1] = self.memory[0][-1][0:self.counter]
            self.memory[1][-1] = self.memory[1][-1][0:self.counter]
        else:
            self.memory[0].pop(-1)
            self.memory[1].pop(-1)
        self.memory = (np.concatenate(self.memory[0]),np.concatenate(self.memory[1]))
        

    def compute_ground_truth(self,notes):
        if self.counter < 50:
            return
        img,time_of_img = self.memory
        game_end_time,end_idx = time_of_img[-1],time_of_img.shape[0]-1
        ground_truth = np.zeros((time_of_img.shape[0],4),dtype=np.bool)
        for section in notes:
            if section['mustHitSection']:
                section_notes = section['sectionNotes']
                for note in section_notes:
                    note_start_time = note[0]/1000
                    note_type = note[1]
                    if game_end_time - note_start_time < 0 or note_type > 3:
                        continue
                    duration = note[2]/1000
                    note_start_dist = np.abs(time_of_img-note_start_time)
                    note_start_idx = np.argmin(note_start_dist)-1
                    note_end_idx = note_start_idx+1
                    if duration:
                        note_end = np.abs(time_of_img-note_start_time-duration)
                        note_end_idx = np.argmin(note_end)
                    ground_truth[note_start_idx:note_end_idx,note_type] = 1
        img_with_key = img[ground_truth.sum(axis=1)>=1]
        img_without_key = img[ground_truth.sum(axis=1)==0]
        x = np.concatenate([img_with_key,
                                img_without_key[np.random.choice(img_without_key.shape[0],size=img_with_key.shape[0]*2+self.base)]])
        y = np.zeros((x.shape[0],4),dtype=np.bool)
        y[0:img_with_key.shape[0]] = ground_truth[ground_truth.sum(axis=1)>=1]
        training_data_x,training_data_y = self.training_data
        
        for i in range(4):
            start = self.training_data_counter%self.capacity
            length = min(self.capacity-self.training_data_counter%self.capacity,x.shape[0])
            end = start + length
            training_data_x[start:end] += x[:,i]
            training_data_y[start:end] += y[:,i]
            self.training_data_counter += length
    def get_data(self):
        return self.training_data[0][:min(self.capacity,self.training_data_counter)],self.training_data[1][:min(self.capacity,self.training_data_counter)]
    def get_data_size(self):
        return self.training_data_counter
    def save(self):
        path = "./memory/"
        with open('./memory/counter.txt', "w") as myfile:
            myfile.write(str(self.training_data_counter))
        np.save(path+"x", self.training_data[0])
        np.save(path+"y", self.training_data[1])
        return 
    def load(self):
        print("loading data")
        path = "./memory/"
        try:
            self.training_data = (np.load(path+"x.npy"),np.load(path+"y.npy"))
            with open('./memory/counter.txt', "r") as myfile:
                self.training_data_counter = int(myfile.read())
        except Exception as e:
            print(e)
            print("load memory failed, restart")
            self.training_data = (np.zeros((self.capacity*4,self.h,self.arrow_width,self.c),dtype=np.uint8),np.zeros((self.capacity,),dtype=np.bool))
            self.training_data_counter = 0


    