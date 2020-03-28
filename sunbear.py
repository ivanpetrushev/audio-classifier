#!/usr/bin/python3
# -*- coding: utf-8 -*-
# based on SunBear's code from:
# https://stackoverflow.com/questions/54081159/how-do-i-link-an-mp3-file-with-a-slider-so-that-the-slider-moves-in-relation-to

from mutagen.mp3 import MP3
from mutagen import MutagenError
from pygame import mixer
import tkinter as tk
import json
import os


class MusicPlayer(tk.Frame):

    def __init__(self, master, filename='sample.mp3', *args, **kwargs):
        super().__init__(master)  # initilizes self, which is a tk.Frame
        self.pack()

        self.master = master
        self.track = filename
        self.track_length = None
        self.current_tag_start = None
        self.current_tag_end = None
        self.player = None
        self.btn_play = None
        self.btn_stop = None
        self.slider = None
        self.slider_value = None
        self.listbox = None
        self.btn_remove_listbox = None
        self.btn_tag_start_stop = None
        self.btn_tag_start_stop_text = None
        self.btn_save_tag = None
        self.field_tags = None
        self.field_tags_value = None

        self.json_filename = filename.replace('.mp3', '.json')
        self.data = []

        # Call these methods
        self.get_audiofile_metadata()
        self.load_audiofile()
        self.load_datafile()
        self.create_widgets()
        self.update_listbox()

    def get_audiofile_metadata(self):
        '''Get audio file and it's meta data (e.g. tracklength).'''
        try:
            f = MP3(self.track)
        except MutagenError:
            print("Fail to load audio file ({}) metadata".format(self.track))
        else:
            track_length = f.info.length
        self.track_length = track_length
        print('self.trackLength', type(self.track_length), self.track_length, ' sec')

    def load_audiofile(self):
        '''Initialise pygame mixer, load audio file and set volume.'''
        player = mixer
        player.init(frequency=48000) # probably we need metadata.info.sample_rate here
        player.music.load(self.track)
        player.music.set_volume(.25)

        self.player = player

    def load_datafile(self):
        '''Loads JSON data for this audio file'''
        if os.path.exists(self.json_filename):
            with open(self.json_filename, encoding='utf-8') as file:
                self.data = json.load(file)

    def write_datafile(self):
        '''Saves JSON data for this audio file'''
        with open(self.json_filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def create_widgets(self):
        '''Create Buttons (e.g. Start & Stop ) and Progress Bar.'''
        self.btn_play = tk.Button(self, text='Play', command=self.play)
        self.btn_play.pack()

        self.btn_stop = tk.Button(self, text='Stop', command=self.stop)
        self.btn_stop.pack()

        self.slider_value = tk.DoubleVar()
        self.slider = tk.Scale(self, to=self.track_length, orient=tk.HORIZONTAL, length=700,
                               resolution=0.5, showvalue=True, tickinterval=30, digit=4,
                               variable=self.slider_value, command=self.update_slider)
        self.slider.pack()

        self.btn_tag_start_stop_text = tk.StringVar()
        self.btn_tag_start_stop_text.set('Tag Start')
        self.btn_tag_start_stop = tk.Button(self, textvariable=self.btn_tag_start_stop_text,
                                            command=self.tag_start_stop)
        self.btn_tag_start_stop.pack()

        self.field_tags_value = tk.StringVar()
        self.field_tags_value.set('Tags (comma separated)')
        self.field_tags = tk.Entry(self, textvariable=self.field_tags_value)
        self.field_tags.pack(fill=tk.BOTH, expand=1)

        self.btn_save_tag = tk.Button(self, text='Save', command=self.save_tag)
        self.btn_save_tag.pack()

        self.btn_remove_listbox = tk.Button(self, text='Remove', command=self.remove_data)
        self.btn_remove_listbox.pack()

        list_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self, yscrollcommand=list_scrollbar.set)
        self.listbox.bind('<Double-Button-1>', self.select_item)
        list_scrollbar.config(command=self.listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def remove_data(self):
        sel = self.listbox.curselection()
        if len(sel) == 0:
            return
        idx = sel[0]
        self.data.pop(idx)
        self.write_datafile()
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.data:
            self.listbox.insert(tk.END, '{i[start]}:{i[end]} - {i[tag]}'.format(i=item))

    def play(self):
        '''Play track from slider location.'''
        playtime = self.slider_value.get()
        self.player.music.play(start=playtime)
        self.track_play(playtime)

    def track_play(self, playtime):
        '''Slider to track the playing of the track.'''
        if self.player.music.get_busy():
            self.slider_value.set(playtime)
            playtime += 1.0
            self.loopID = self.after(1000, lambda: self.track_play(playtime))
        else:
            print('Track Ended')

    def select_item(self, *event):
        sel = self.listbox.curselection()
        if len(sel) == 0:
            return
        idx = sel[0]
        start = self.data[idx]['start']
        end = self.data[idx]['end']
        tag = self.data[idx]['tag']
        self.current_tag_start = start
        self.current_tag_end = end
        self.slider_value.set(start)
        self.field_tags_value.set(tag)
        self.btn_tag_start_stop_text.set('Tag Stop')

    def update_slider(self, value):
        '''Move slider position when tk.Scale's trough is clicked or when slider is clicked.'''
        if self.player.music.get_busy():
            self.after_cancel(self.loopID)  # Cancel PlayTrack loop
            self.slider_value.set(value)  # Move slider to new position
            self.play()  # Play track from new postion
        else:
            self.slider_value.set(value)  # Move slider to new position

    def stop(self):
        '''Stop the playing of the track.'''
        if self.player.music.get_busy():
            self.player.music.stop()

    def tag_start_stop(self):
        if not self.current_tag_start:
            self.current_tag_start = self.slider_value.get()
            self.btn_tag_start_stop_text.set('Tag Stop')
            return
        self.current_tag_end = self.slider_value.get()
        self.player.music.stop()

    def save_tag(self):
        self.data.append({
            'start': self.current_tag_start,
            'end': self.current_tag_end,
            'tag': self.field_tags_value.get()
        })
        self.current_tag_start = None
        self.current_tag_end = None
        self.field_tags_value.set('Tags (comma separated)')
        self.btn_tag_start_stop_text.set('Tag Start')
        self.write_datafile()
        self.update_listbox()


if __name__ == "__main__":
    root = tk.Tk()  # Initialize an instance of Tk window.
    app = MusicPlayer(root)  # Initialize an instance of MusicPlayer object and passing Tk window instance into it as it's master.
    root.mainloop()
