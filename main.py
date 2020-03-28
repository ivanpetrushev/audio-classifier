from sunbear import MusicPlayer
import tkinter as tk
import sys

filename = 'sample.mp3'
if len(sys.argv) > 1:
    filename = sys.argv[1]

root = tk.Tk()
root.geometry("800x600")
app = MusicPlayer(root, filename=filename)
root.mainloop()
