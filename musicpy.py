from cmath import exp
from msilib.schema import Directory, ListBox
import os
import sys
import pygame
from tkinter import *
from tkinter.ttk import Scale
from tkinter.filedialog import askdirectory
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import song_feeder

root = Tk()
# root.minsize(300,300)

player_frame = Frame(root)

song_paths = []
song_titles = []
# DIRECTORY = 'C:\\Users\\jdubo\\Music\\D.J. JACKSON 108.9 FM'
DIRECTORY = 'C:\\Program Files\\Rockstar Games\\Grand Theft Auto V\\scripts\\Custom Radio Stations\\GTA Custom\\D.J. JACKSON 108.9 FM'

def directorychooser():
    # directory = askdirectory()
    directory = DIRECTORY
    os.chdir(directory)

    for files in os.listdir(directory):
        if files.endswith(".mp3"):

            realdir = os.path.realpath(files)
            audio = ID3(realdir)

            try:
                song_titles.append(audio['TIT2'].text[0])
            except KeyError:
                song_titles.append(files[:-4])

            song_paths.append(files)

def init():
    pygame.mixer.init()
    # pygame.mixer.music.load(song_paths[0])
    # pygame.mixer.music.play()

# ---------         Player Frame         ---------
# --- Variables   ---
v = StringVar()
song_lenth = 0.0
index = 0
time_offset = 0.0
status = 'playing'

# ---   Functions   ---
def updatelabel():
    global index, songname, song_lenth
    songs_listbox.selection_clear(0, END)
    v.set(song_titles[index])
    songs_listbox.selection_set(index)
    song_lenth = MP3(song_paths[index]).info.length * 1000
    update_slider(song_titles[index])
    #return songname

def nextsong(event):
    global index
    index = (index + 1) % len(song_paths)
    pygame.mixer.music.load(song_paths[index])
    pygame.mixer.music.play()
    updatelabel()

def prevsong(event):
    global index
    index = (index - 1 + len(song_paths)) % len(song_paths)
    pygame.mixer.music.load(song_paths[index])
    pygame.mixer.music.play()
    updatelabel()

def songat(event):
    global index
    index = songs_listbox.curselection()[0]
    pygame.mixer.music.load(song_paths[index])
    pygame.mixer.music.play()
    updatelabel()

def unpausesong(event):
    global status
    pygame.mixer.music.unpause()
    #pausebutton.config(text="pause song")
    status = 'playing'
    v.set("Song unpasued")
    #return songname

def pausesong(event):
    global status
    pygame.mixer.music.pause()
    status = 'paused'
    v.set("Song Paused")
    #pausebutton.config(text="unpasue song")
    #return songname

def stopsong(event):
    global status
    pygame.mixer.music.stop()
    v.set("")
    status = 'stop'
    raise_frame(artists_frame)
    reset_artist_labels()
    #return songname

def raise_frame(frame):
    updatelabel()
    frame.tkraise()

def reset_songs_list():
    global song_paths, songs_listbox, index, status
    status = 'playing'
    songs_listbox.delete(0, END)
    index = 0
    song_paths.clear()
    song_titles.clear()

def update_slider(song=None):
    global song_lenth, seeker, time_offset

    # Every song only has one slider updater function attatched to it.
    if not song == song_titles[index] or status == 'stopped':
        time_offset = 0.0
        return

    if not pygame.mixer.music.get_busy() and status == 'playing':
        nextsong(None)
    
    position = time_offset + pygame.mixer.music.get_pos()
    seeker.config(value=position/song_lenth)

    label.after(1000, update_slider, song)

def slide(duration):
    global time_offset
    time_offset = (float(duration) * song_lenth) - pygame.mixer.music.get_pos()

    try:
        pygame.mixer.music.set_pos(float(duration) * (song_lenth / 1000))
    except pygame.error:
        nextsong(None)

# ---   Components   ---
label = Label(player_frame,text='Music Player')
label.pack(expand=True, fill='x', pady=10)

# Songs Listbox
songs_listbox = Listbox(player_frame)
songs_listbox.configure(font='TkFixedFont')
songs_listbox.pack(expand=True,fill=BOTH,padx=10)

# Song label
songlabel = Label(player_frame,textvariable = v,width = 35)
songlabel.pack(expand=True,fill='x',pady=(10,0))

player_menu_frame = Frame(player_frame)

# Previous Button
previousbutton = Button(player_menu_frame,text = '<<')
previousbutton.pack(side=LEFT, padx=5)

# Next Button
nextbutton = Button(player_menu_frame,text = '>>')
nextbutton.pack(side=LEFT, padx=5)

# PauseButton
pausebutton = Button(player_menu_frame, text= '||')
pausebutton.pack(side=LEFT, padx=5)

# Unpause Button
unpausebutton = Button(player_menu_frame, text= 'Play')
unpausebutton.pack(side=LEFT, padx=5)

# Stop Button
stopbutton = Button(player_menu_frame,text='Stop Music')
stopbutton.pack(side=LEFT, padx=5)

# Time Seeker
seeker = Scale(player_frame, orient=HORIZONTAL, command=slide)
seeker.pack(expand=True, fill='x', pady=5)

player_menu_frame.pack(side=BOTTOM,padx=10,pady=(0,10))
player_frame.grid(row=0, column=0, sticky='nesw')

# ---   Binds   ---
songs_listbox.bind('<Double-1>',songat)

nextbutton.bind("<Button-1>",nextsong)
previousbutton.bind("<Button-1>",prevsong)
pausebutton.bind("<Button-1>",pausesong)
unpausebutton.bind("<Button-1>",unpausesong)
stopbutton.bind("<Button-1>",stopsong)
# ---------         Player Frame         ---------

# ---------         Artist Chooser Frame         ---------
# ---   Variables   ---
full_artist_list = song_feeder.get_artists() # The full list of all artists.
artist_list = [] # The dynamic artist list.
chosen_artists = [] # The current list of artists which are chosen.
sv = StringVar()
last_artist = None

# ---   Functions   ---
# Event when an artist is double clicked in the listbox.
def choose_artist(event):
    global index, chosen_artists, last_artist
    index = artists_listbox.curselection()[0]
    last_artist = artist_list[index]
    if (artist_list[index] not in chosen_artists):
        chosen_artists.append(artist_list[index])
        change_artist_labels()

def filter_artists(a1, a2, mode):
    artist_list.clear()

    for artist in full_artist_list:
        if not sv.get() or sv.get().lower() in artist.lower():
            artist_list.append(artist)

    change_artist_labels()
    # reset_artist_labels()

# Resets the artist listbox.
def reset_artist_labels():
    global chosen_artists, last_artist
    last_artist = None
    chosen_artists.clear()
    change_artist_labels()

# Updates all the labels in the artists listbox.
def change_artist_labels():
    artists_listbox.delete(0, END)

    for artist in artist_list:
        artists_listbox.insert(END, artist)

    if last_artist:
        fts = song_feeder.get_fts(last_artist)

    length = range(len(artist_list))
    for i in length:
        if last_artist:
            if artist_list[i] in fts:
                artists_listbox.itemconfig(i, background='green')

        try:
            index = chosen_artists.index(artist_list[i])
            artist = artist_list[i]
            artists_listbox.delete(i)
            artists_listbox.insert(i, '{} {}'.format(artist[:25].ljust(25), index))
            artists_listbox.itemconfig(i, background='gray')
        except:
            pass

def load_songs(event):
    global song_paths, songs_listbox, chosen_artists
    reset_songs_list()

    player_frame.tkraise()
    songs = song_feeder.generate_songs_list(chosen_artists)
    labels = []

    for song in songs:
        song_paths.append('{}\\{}'.format(DIRECTORY, song))

    for items in songs:
        audio = ID3('{}\\{}'.format(DIRECTORY, items))
        song_name = items[:-4]
        artist = None

        if 'TIT2' in audio.keys():
            song_name = audio['TIT2'].text[0]

        if 'TPE1' in audio.keys():
            artist = audio['TPE1'].text[0]
        
        labels.append('{} | {}'.format(artist[:10].split('/')[0].ljust(10), song_name.ljust(20)))
        song_titles.insert(0,song_name)

    labels.reverse()
    for label in labels:
        songs_listbox.insert(0,label)

    song_titles.reverse()

    pygame.mixer.music.load(song_paths[0])
    pygame.mixer.music.play()
    updatelabel()

# ---   Components   ---
artists_frame = Frame(root)

search_entry = Entry(artists_frame, textvariable=sv)
search_entry.pack(expand=True, fill='x', padx=10, pady=(0,0))

artists_listbox = Listbox(artists_frame)
artists_listbox.configure(font='TkFixedFont')
artists_listbox.pack(padx=10, pady=10)

artists_menu_frame = Frame(artists_frame)

filterbutton = Button(artists_menu_frame,text='Filter')
filterbutton.pack(side=LEFT, padx=5)

playlistbutton = Button(artists_menu_frame,text='Play Songs')
playlistbutton.pack(side=LEFT, padx=5)

artists_menu_frame.pack(side=BOTTOM, pady=(0,10))

artists_frame.grid(row=0, column=0, sticky='nesw')

# ---   Binds   ---
sv.trace('w', filter_artists)
artists_listbox.bind("<Double-1>",choose_artist) # Listbox
filterbutton.bind("<Button-1>",filter_artists) # Filter Button
playlistbutton.bind("<Button-1>",load_songs) # Play Button

songs_listbox.bind("<w>",lambda event : pygame.mixer.music.set_volume(min(pygame.mixer.music.get_volume() + 0.1, 1.0)))
songs_listbox.bind("<s>",lambda event : pygame.mixer.music.set_volume(max(pygame.mixer.music.get_volume() - 0.1, 0.0)))

reset_artist_labels()
filter_artists(None, None, None)
# ---------         Artist Chooser Frame         ---------

def main():
    flag = ''
    
    init()

    for arg in sys.argv:
        if flag == '-V':
            if flag == '-V':
                pygame.mixer.music.set_volume(float(arg))
            flag = '-V'

        flag = arg
            
    # directorychooser()
    
    player_frame.mainloop() 

if __name__ == '__main__':
    main()
