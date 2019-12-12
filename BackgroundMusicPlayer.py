from pygame import mixer
from random import randint
import os
from mutagen.mp3 import MP3
import time


class MusicPlayer:
    def __init__(self):
        mixer.init()
        self.path = os.getcwd() + r'\audio\menumusic'
        self.song_list = []

    def update_song_list(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                filename = os.path.join(root, file)
                if filename.endswith('.mp3'):
                    self.song_list.append(filename)
        return

    def play_song(self):
        selected_song = self.song_list[randint(0, len(self.song_list) - 1)]
        mixer.music.load(selected_song)
        mixer.music.play()
        return selected_song


    def get_song_length(self, selected_song):
        lengthofSong = int(MP3(selected_song).info.length)  # because the real length of the song is float
        return lengthofSong


    def secPlus(self, counter):
        time.sleep(1)
        counter += 1
        return counter

    def songPlayer(self):
        counter = 0
        newRound = True
        while True:
            if newRound:
                self.update_song_list()
                da_song = self.play_song()
                newRound = False

            counter = self.secPlus(counter)
            if counter == self.get_song_length(da_song):
                newRound = True
                counter = 0
            #print(f"counter: {counter}. time to new Song: {self.get_song_length(da_song) - counter}")


if __name__ == "__main__":
    myplr = MusicPlayer()
    myplr.songPlayer()


