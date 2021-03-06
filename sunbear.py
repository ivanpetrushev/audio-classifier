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
from datetime import datetime
from random import randint


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
        self.slider = None
        self.slider_value = None
        self.slider_last_updated_ts = 0
        self.slider_update_threshold_ms = 40  # to avoid ALSA underrun errors
        self.listbox = None
        self.btn_play = None
        self.btn_10_left = None
        self.btn_10_right = None
        self.btn_remove_listbox = None
        self.btn_set_tag_start = None
        self.btn_set_tag_stop = None
        self.btn_save_tag = None
        self.btn_cancel_current = None
        self.field_tags = None
        self.field_tags_value = None
        self.field_tags_default_value = 'Tags (comma separated)'
        self.overview_canvas = None
        self.label_info = None
        self.label_current = None
        self.label_current_value = None

        self.icon_play = None
        self.icon_rec = None
        self.icon_cancel = None
        self.icon_pause = None
        self.icon_plus = None
        self.icon_minus = None

        self.json_filename = filename.replace('.mp3', '.json')
        self.data = []
        self.is_playing = False

        # Call these methods
        self.get_audiofile_metadata()
        self.load_audiofile()
        self.load_datafile()
        self.create_widgets()
        self.update_listbox()
        self.update_overview()

        self.play_pause()

    def get_audiofile_metadata(self):
        '''Get audio file and it's meta data (e.g. tracklength).'''
        try:
            f = MP3(self.track)
        except MutagenError:
            print("Fail to load audio file ({}) metadata".format(self.track))
        else:
            track_length = f.info.length
        self.track_length = track_length

    def load_audiofile(self):
        '''Initialise pygame mixer, load audio file and set volume.'''
        player = mixer
        player.init(frequency=48000)  # probably we need metadata.info.sample_rate here
        print('Loading audio file:', self.track)
        player.music.load(self.track)
        # player.music.set_volume(.25)
        self.player = player

    def load_datafile(self):
        '''Loads JSON data for this audio file'''
        print('Loading data file:', self.json_filename)
        if os.path.exists(self.json_filename):
            with open(self.json_filename, encoding='utf-8') as file:
                self.data = json.load(file)
        else:
            print('Data file not found, will be created on data update')

    def write_datafile(self):
        '''Saves JSON data for this audio file'''
        with open(self.json_filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def data_updated(self):
        self.data = sorted(self.data, key=lambda i: i['start'])
        self.write_datafile()
        self.update_listbox()
        self.update_overview()

    def update_overview(self):
        self.update()
        self.overview_canvas.delete(tk.ALL)
        k = self.overview_canvas.winfo_width() / self.track_length
        for item in self.data:
            y = randint(0, 20)
            x_start = k * item['start']
            x_end = k * item['end']
            self.overview_canvas.create_line(x_start, y, x_end, y, width=5)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.data:
            duration = item['end'] - item['start']
            duration = round(duration * 10) / 10
            # formatting spaces can be ugly in non-monospaced font
            self.listbox.insert(tk.END,
                                '{i[start]:>7} {i[end]:>7} {duration:>6}s {i[tag]}'.format(i=item, duration=duration))

    def update_label_current(self):
        self.label_current_value.set('Current tag: start: ' + str(self.current_tag_start) + ', end: ' + str(self.current_tag_end))

    def create_widgets(self):
        '''Create Buttons (e.g. Start & Stop ) and Progress Bar.'''
        self.icon_play = tk.PhotoImage(file='img/play.png')
        self.icon_rec = tk.PhotoImage(file='img/rec.png')
        self.icon_cancel = tk.PhotoImage(file='img/cancel.png')
        self.icon_pause = tk.PhotoImage(file='img/pause.png')
        self.icon_plus = tk.PhotoImage(file='img/plus.png')
        self.icon_minus = tk.PhotoImage(file='img/minus.png')

        self.label_info = tk.Label(self, text='Playing: ' + self.track)
        self.label_info.pack()

        self.btn_play = tk.Button(self, text='Play/Pause', command=self.play_pause, image=self.icon_pause,
                                  compound=tk.LEFT)
        self.btn_play.pack()

        subframe_10 = tk.Frame(self)
        self.btn_10_left = tk.Button(subframe_10, text='-10s', command=self.seek_10_left)
        self.btn_10_left.pack(side=tk.LEFT)

        self.btn_10_right = tk.Button(subframe_10, text='+10s', command=self.seek_10_right)
        self.btn_10_right.pack(side=tk.RIGHT)
        subframe_10.pack()

        self.slider_value = tk.DoubleVar()
        self.slider = tk.Scale(self, to=self.track_length, orient=tk.HORIZONTAL, length=1200,
                               resolution=0.5, showvalue=True,  # tickinterval=30, digit=4,
                               variable=self.slider_value, command=self.update_slider)
        self.slider.pack()

        self.overview_canvas = tk.Canvas(self, height=20)
        self.overview_canvas.pack(fill=tk.BOTH, expand=1)

        subframe = tk.Frame(self)
        self.btn_set_tag_start = tk.Button(subframe, text="Set Tag Start",
                                          command=self.set_tag_start, image=self.icon_play,
                                          compound=tk.LEFT)
        self.btn_set_tag_start.pack(side=tk.LEFT)

        self.btn_set_tag_stop = tk.Button(subframe, text="Set Tag Stop",
                                            command=self.set_tag_stop, image=self.icon_pause,
                                            compound=tk.LEFT)
        self.btn_set_tag_stop.pack(side=tk.LEFT)

        self.btn_cancel_current = tk.Button(subframe, text='Clear Current', command=self.cancel_current,
                                            image=self.icon_cancel,
                                            compound=tk.LEFT)
        self.btn_cancel_current.pack(side=tk.RIGHT)
        subframe.pack()

        self.label_current_value = tk.StringVar(value='Current tag:')
        self.label_current = tk.Label(self, textvariable=self.label_current_value, anchor='w')
        self.label_current.pack(fill=tk.BOTH, expand=1)

        self.field_tags_value = tk.StringVar()
        self.field_tags_value.set(self.field_tags_default_value)
        self.field_tags = tk.Entry(self, textvariable=self.field_tags_value)
        self.field_tags.pack(fill=tk.BOTH, expand=1)

        self.btn_save_tag = tk.Button(self, text='Save', command=self.save_tag, image=self.icon_plus, compound=tk.LEFT)
        self.btn_save_tag.pack()

        self.btn_remove_listbox = tk.Button(self, text='Remove', command=self.remove_data, image=self.icon_minus, compound=tk.LEFT)
        self.btn_remove_listbox.pack()

        list_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self, height=30, yscrollcommand=list_scrollbar.set)
        # sorry for the ugly font! I need monospace for formatting!
        self.listbox.config(font=('Courier', 12))
        self.listbox.bind('<Double-Button-1>', self.select_item)
        list_scrollbar.config(command=self.listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # control change commands (button click, slider move, etc.)
    def play_pause(self):
        '''Play track from slider location.'''
        if self.is_playing:
            # play -> pause
            self.btn_play.configure(image=self.icon_play)
            if self.player.music.get_busy():
                self.player.music.stop()
        else:
            # pause -> play
            self.btn_play.configure(image=self.icon_pause)
            playtime = self.slider_value.get()
            self.player.music.play(start=playtime)
            self.track_play(playtime)
        self.is_playing = not self.is_playing

    def seek_10_left(self):
        value = str(int(self.slider_value.get()) - 10)
        self.update_slider(value)

    def seek_10_right(self):
        value = str(int(self.slider_value.get()) + 10)
        self.update_slider(value)

    def update_slider(self, value):
        '''Move slider position when tk.Scale's trough is clicked or when slider is clicked.'''

        # throttle updating to once in N ms, otherwise we will get ALSA underrun errors
        dt = datetime.now()
        now_ts = dt.timestamp()
        threshold_ts = self.slider_update_threshold_ms / 1000
        if now_ts - self.slider_last_updated_ts < threshold_ts:
            return
        self.slider_last_updated_ts = now_ts

        if self.player.music.get_busy():
            self.after_cancel(self.loopID)  # Cancel PlayTrack loop
            self.slider_value.set(value)  # Move slider to new position
            self.is_playing = False
            self.play_pause()  # Play track from new postion
        else:
            self.slider_value.set(value)  # Move slider to new position

    def set_tag_start(self):
        self.current_tag_start = self.slider_value.get()
        self.update_label_current()

    def set_tag_stop(self):
        self.current_tag_end = self.slider_value.get()
        self.update_label_current()
        self.player.music.stop()

    def cancel_current(self):
        self.current_tag_start = None
        self.current_tag_end = None
        self.field_tags_value.set(self.field_tags_default_value)
        self.update_label_current()

    def save_tag(self):
        self.data.append({
            'start': self.current_tag_start,
            'end': self.current_tag_end,
            'tag': self.field_tags_value.get()
        })
        self.data_updated()
        self.current_tag_start = None
        self.current_tag_end = None
        self.field_tags_value.set(self.field_tags_default_value)
        self.update_label_current()

    def remove_data(self):
        sel = self.listbox.curselection()
        if len(sel) == 0:
            return
        idx = sel[0]
        self.data.pop(idx)
        self.data_updated()

    # end of commands

    def track_play(self, playtime):
        '''Slider to track the playing of the track.'''
        if self.player.music.get_busy():
            self.slider_value.set(playtime)
            playtime += 1.0
            self.loopID = self.after(1000, lambda: self.track_play(playtime))

    def select_item(self, *event):
        sel = self.listbox.curselection()
        if len(sel) == 0:
            return
        idx = sel[0]
        item = self.data[idx]
        start = item['start']
        end = item['end']
        tag = item['tag']
        self.current_tag_start = start
        self.current_tag_end = end
        self.slider_value.set(start)
        self.field_tags_value.set(tag)
        self.update_label_current()
        self.is_playing = True
        self.play_pause()  # Play track from new postion


if __name__ == "__main__":
    root = tk.Tk()  # Initialize an instance of Tk window.
    app = MusicPlayer(root)  # Initialize an instance of MusicPlayer object and passing Tk window instance into it as it's master.
    root.mainloop()
