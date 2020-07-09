import os
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog

from tkinter import ttk
from ttkthemes import themed_tk as tk

from mutagen.mp3 import MP3
from pygame import mixer


class App():
    def __init__(self):
        self.filename_path = ""
        self.paused = False
        self.muted = False

        self.init_elements()

    def init_elements(self):
        self.root = tk.ThemedTk()
        self.root.get_themes()                 # Returns a list of all themes that can be set
        self.root.set_theme("radiance")         # Sets an available theme

        # Fonts - Arial (corresponds to Helvetica), Courier New (Courier), Comic Sans MS, Fixedsys,
        # MS Sans Serif, MS Serif, Symbol, System, Times New Roman (Times), and Verdana
        #
        # Styles - normal, bold, roman, italic, underline, and overstrike.

        self.statusbar = ttk.Label(self.root, text="Welcome to Melody", relief=SUNKEN, anchor=W, font='Times 10 italic')
        self.statusbar.pack(side=BOTTOM, fill=X)

        # Create the self.menubar
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        # Create the submenu

        self.subMenu = Menu(self.menubar, tearoff=0)

        self.playlist = []
        # playlist - contains the full path + filename
        # self.playlistbox - contains just the filename
        # Fullpath + filename is required to play the music inside play_music load function

        self.menubar.add_cascade(label="File", menu=self.subMenu)
        self.subMenu.add_command(label="Open", command=self.browse_file)
        self.subMenu.add_command(label="Exit", command=self.root.destroy)

        self.subMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.subMenu)
        self.subMenu.add_command(label="About Us", command=self.about_us)

        mixer.init()  # initializing the mixer

        self.root.title("Melody")
        # Root Window - StatusBar, LeftFrame, RightFrame
        # LeftFrame - The listbox (playlist)
        # RightFrame - TopFrame,MiddleFrame and the BottomFrame

        Label(self.root, text="Ingresar audio").pack(side=TOP, anchor=W, fill=X, expand=YES)

        self.leftframe = Frame(self.root)
        self.leftframe.pack(side=LEFT, padx=30, pady=30)

        self.playlistbox = Listbox(self.leftframe)
        self.playlistbox.pack()

        self.addBtn = ttk.Button(self.leftframe, text="+ Add", command=self.browse_file)
        self.addBtn.pack(side=LEFT)

        self.delBtn = ttk.Button(self.leftframe, text="- Del", command=self.del_song)
        self.delBtn.pack(side=LEFT)

        self.rightframe = Frame(self.root)
        self.rightframe.pack(pady=30)

        self.topframe = Frame(self.rightframe)
        self.topframe.pack()

        self.lengthlabel = ttk.Label(self.topframe, text='Total Length : --:--')
        self.lengthlabel.pack(pady=5)

        self.currenttimelabel = ttk.Label(self.topframe, text='Current Time : --:--', relief=GROOVE)
        self.currenttimelabel.pack()

        self.middleframe = Frame(self.rightframe)
        self.middleframe.pack(pady=30, padx=30)

        self.playPhoto = PhotoImage(file='src/images/play2.png')
        self.playBtn = ttk.Button(self.middleframe, image=self.playPhoto, command=self.play_music)
        self.playBtn.grid(row=0, column=0, padx=10)

        self.stopPhoto = PhotoImage(file='src/images/stop2.png')
        self.stopBtn = ttk.Button(self.middleframe, image=self.stopPhoto, command=self.stop_music)
        self.stopBtn.grid(row=0, column=1, padx=10)

        self.pausePhoto = PhotoImage(file='src/images/pause2.png')
        self.pauseBtn = ttk.Button(self.middleframe, image=self.pausePhoto, command=self.pause_music)
        self.pauseBtn.grid(row=0, column=2, padx=10)

        # Bottom Frame for volume, rewind, mute etc.

        self.bottomframe = Frame(self.rightframe)
        self.bottomframe.pack()

        self.rewindPhoto = PhotoImage(file='src/images/rewind2.png')
        self.rewindBtn = ttk.Button(self.bottomframe, image=self.rewindPhoto, command=self.rewind_music)
        self.rewindBtn.grid(row=0, column=0)

        self.mutePhoto = PhotoImage(file='src/images/mute2.png')
        self.volumePhoto = PhotoImage(file='src/images/volume2.png')
        self.volumeBtn = ttk.Button(self.bottomframe, image=self.volumePhoto, command=self.mute_music)
        self.volumeBtn.grid(row=0, column=1)

        self.scale = ttk.Scale(self.bottomframe, from_=0, to=100, orient=HORIZONTAL, command=self.set_vol)
        self.scale.set(70)  # implement the default value of scale when music player starts
        mixer.music.set_volume(0.7)
        self.scale.grid(row=0, column=2, pady=15, padx=30)

        self.confirmButton = ttk.Button(self.root, text="Detectar emociones", command=self.detect).pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def detect(self):
        try:
            selected_song = self.playlistbox.curselection()
            selected_song = int(selected_song[0])
            play_it = self.playlist[selected_song]
            print(play_it)
        except:
            print("Error, audio no seleccionado")

    def browse_file(self):
        self.filename_path = filedialog.askopenfilename(initialdir = "/", title = "Seleccionar audio", filetypes = [("Audio files", ".wav")])
        self.add_to_playlist(self.filename_path)

        mixer.music.queue(self.filename_path)


    def add_to_playlist(self, filename):
        filename = os.path.basename(filename)
        index = 0
        self.playlistbox.insert(index, filename)
        self.playlist.insert(index, self.filename_path)
        index += 1


    def about_us(self):
        tkinter.messagebox.showinfo('About Melody', 'This is a music player build using Python Tkinter by @attreyabhatt')

    def del_song(self):
        selected_song = self.playlistbox.curselection()
        selected_song = int(selected_song[0])
        self.playlistbox.delete(selected_song)
        self.playlist.pop(selected_song)

    def show_details(self, play_song):
        file_data = os.path.splitext(play_song)

        if file_data[1] == '.mp3':
            audio = MP3(play_song)
            total_length = audio.info.length
        else:
            a = mixer.Sound(play_song)
            total_length = a.get_length()

        # div - total_length/60, mod - total_length % 60
        mins, secs = divmod(total_length, 60)
        mins = round(mins)
        secs = round(secs)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        self.lengthlabel['text'] = "Total Length" + ' - ' + timeformat

        self.t1 = threading.Thread(target=self.start_count, args=(total_length,))
        self.t1.start()


    def start_count(self, t):
        # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
        # Continue - Ignores all of the statements below it. We check if music is paused or not.
        current_time = 0
        while current_time <= t and mixer.music.get_busy():
            if self.paused:
                continue
            else:
                mins, secs = divmod(current_time, 60)
                mins = round(mins)
                secs = round(secs)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                self.currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
                time.sleep(1)
                current_time += 1


    def play_music(self):
        if self.paused:
            mixer.music.unpause()
            self.statusbar['text'] = "Music Resumed"
            self.paused = False
        else:
            try:
                self.stop_music()
                time.sleep(1)
                selected_song = self.playlistbox.curselection()
                selected_song = int(selected_song[0])
                play_it = self.playlist[selected_song]
                mixer.music.load(play_it)
                mixer.music.play()
                self.statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
                self.show_details(play_it)
            except:
                tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')


    def stop_music(self):
        mixer.music.stop()
        self.statusbar['text'] = "Music Stopped"


    def pause_music(self):
        self.paused = True
        mixer.music.pause()
        self.statusbar['text'] = "Music Paused"


    def rewind_music(self):
        self.play_music()
        self.statusbar['text'] = "Music Rewinded"


    def set_vol(self, val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)
        # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1

    def mute_music(self):
        if self.muted:  # Unmute the music
            mixer.music.set_volume(0.7)
            self.volumeBtn.configure(image=self.volumePhoto)
            self.scale.set(70)
            self.muted = False
        else:  # mute the music
            mixer.music.set_volume(0)
            self.volumeBtn.configure(image=self.mutePhoto)
            self.scale.set(0)
            self.muted = True

    def on_closing(self):
        self.stop_music()
        self.root.destroy()
        self.t1.join() 
        if self.t1.isAlive(): 
            print('thread still alive')

if __name__ == "__main__":
    App()