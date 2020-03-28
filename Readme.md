# audio-classifier

audio-classifier is a Python/Tk tool for easier and visual tagging sections of audio tracks. 
It plays MP3 sounds and saves JSON data.

It is based on the simple Tk audio player from Sunbear: https://stackoverflow.com/questions/54081159/how-do-i-link-an-mp3-file-with-a-slider-so-that-the-slider-moves-in-relation-to

## Requirements

* tkinter - usually shipped with Python
* mutagen - audio metadata extraction library - `pip3 install mutagen`

## Usage
> $ python3.6 main.py <audiofile>


JSON data will be saved to external file with the same filename as the source sound.

## Tips

If you have a big number of audio files in a directory, it might be easier to merge all into single audiofile and work with it.

You can combine multiple mp3 files into one with `mp3wrap`. It is good for up to 255 files in directory:
> $ sudo apt install mp3wrap  
> $ mp3wrap output.mp3 dir/*mp3 

You can combine multiple mp3 files into one with `sox`
> $ sudo apt-get install sox libsox-fmt-all  
> $ sox dir/*mp3 output.mp3

Combining files with ffmpeg:
> $ find *.mp3 | sed 's:\ :\\\ :g'| sed 's/^/file /' > fl.txt; ffmpeg -f concat -safe 0 -i fl.txt -c copy output.mp3; rm fl.txt

## Troubleshooting

Alsa error on seek in long files: 
> ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred