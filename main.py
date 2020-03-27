from sunbear import MusicPlayer
import tkinter as tk

FILENAME = 'sample.mp3'

root = tk.Tk()
app = MusicPlayer(root, filename=FILENAME)
root.mainloop()