import json
from game_util import *
class Song_iterator(object):
    def __init__(self,training_set = list(range(0,11))+list(range(16,18)),testing_set=list(range(11,16)),levels = [0,1]):
        self.training_set = training_set
        self.testing_set = testing_set
        self.training_set_size = len(self.training_set)
        self.testing_set_size = len(self.testing_set)
        self.levels = levels

        self.training_idx = 0
        self.testing_idx = 0
        self.current_level = -1
        self.song_list = json.load(open('song_list.json'))['list']

    def get_next_song_info(self):
        self.current_level+=1
        if self.current_level >= len(self.levels):
            self.current_level = 0
            self.training_idx+=1
        if self.training_idx >= self.training_set_size:
            self.training_idx = 0
        song_name = self.song_list[self.training_idx]['name']
        song_length = self.get_song_length(self.get_sections())
        return song_name,self.training_idx,self.current_level,song_length

    def get_sections(self):
        song = self.song_list[self.training_idx]
        folder_name = song['name']
        levels = song['levels']
        file_name = levels[self.current_level]
        
        file_path = './game/assets/data/'+folder_name+'/'+file_name+'.json'
        try:
            notes = json.load(open(file_path))['song']['notes']
        except Exception as e:
            e_str = str(e)
            if 'Extra data' in e_str:
                line_num = int(e_str[e_str.find('line ')+5:e_str.find(' column')])
                col_num = int(e_str[e_str.find('column ')+7:e_str.find(' (')])
                char = int(e_str[e_str.find('char ')+5:len(e_str)-1])
                file = open(file_path)
                file_data = ''
                for i in range(line_num-1):
                    file_data+=file.readline()
                file_data+=file.readline()[:col_num-1]
                file.close()
                notes = json.loads(file_data)['song']['notes']
            else:
                raise Exception('Never seen this one')
        return notes

    def get_song_length(self,sections):
        for section in reversed(sections):
            if section['mustHitSection']:
                section_notes = section['sectionNotes']
                if len(section_notes)>0:
                    last_note = section_notes[-1]
                    return last_note[0]+last_note[2]
        return -1
        

    # def get_testing_song(self):