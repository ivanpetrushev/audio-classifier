# audio-classifier

audio-classifier is a tool for easier and visual tagging sections of audio tracks. 
It plays MP3 sounds and saves JSON data.

It is based on the simple Tk audio player from Sunbear: https://stackoverflow.com/questions/54081159/how-do-i-link-an-mp3-file-with-a-slider-so-that-the-slider-moves-in-relation-to

## Requirements

* tkinter - usually shipped with Python
* mutagen - audio metadata extraction library - `pip3 install mutagen`

## Usage
> $ python3.6 main.py

Check FILENAME constant. 

JSON data will be saved to external file with the same filename as the source sound.