import random
import tensorflow as tf 
from tensorflow import keras
import numpy as np
import os
class FNF_Visual(keras.Model):
    def __init__(self):
        super(FNF_Visual,self).__init__()
        self.net = keras.Sequential([
                                keras.layers.BatchNormalization(),
                                keras.layers.Conv2D(128, (3,3),strides = (2,2), padding = 'valid'),
                                keras.layers.BatchNormalization(),
                                keras.layers.ReLU(),

                                keras.layers.Conv2D(64, (3,3),strides = (1,1), padding = 'valid'),
                                keras.layers.BatchNormalization(),
                                keras.layers.ReLU(),
                                
                                keras.layers.Conv2D(32, (3,3),strides = (1,1), padding = 'valid'),
                                keras.layers.BatchNormalization(),
                                keras.layers.ReLU(),

                                keras.layers.Flatten(),
                                keras.layers.Dense(1024),
                                keras.layers.BatchNormalization(),
                                keras.layers.ReLU(),
                                keras.layers.Dense(512),
                                keras.layers.BatchNormalization(),
                                keras.layers.ReLU(),
                                keras.layers.Dense(1,activation='sigmoid')
                                ])

    def call(self, x):
        x = tf.cast(x,tf.float32)
        y = self.net(x)
        return y

    
    def train_step(self,data):
        x,y=data
        x = tf.cast(x,tf.float32)
        return super().train_step((x,y))
