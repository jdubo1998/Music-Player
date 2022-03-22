import os
import json
from random import choice
from mutagen.id3 import ID3

# DIRECTORY = 'C:\\Users\\jdubo\\Music\\D.J. JACKSON 108.9 FM'
# _file_path = 'C:\\Users\\jdubo\\Documents\\CodingProjects\\Python\\Music-Player\\test\\data.json'
DIRECTORY = 'C:\\Program Files\\Rockstar Games\\Grand Theft Auto V\\scripts\\Custom Radio Stations\\GTA Custom\\D.J. JACKSON 108.9 FM'
_file_path = 'C:\\Users\\\Jacob\\Documents\\CodingProjects\\Python\\Music-Player\\test\\data.json'

_dupe_artists = []

def save_file(data):
    file = open(_file_path, 'w')
    json.dump(data, file, indent=4)
    file.close()

def read_file():
    data = {"songs": [], "artists": {}}

    if not os.path.isfile(_file_path):
        save_file(data)

    else:
        file = open(_file_path, 'r')
        data = json.load(file)
        file.close()

    return data

def generate_tree(directory):
    data = read_file()
    save = False

    for song in os.listdir(directory):
        if song.endswith(".mp3"):
            if song not in data['songs']:
                data['songs'].append(song)
                save = True

                audio = ID3('{}\\{}'.format(directory, song))
                try:
                    # Gets the artists from a song.
                    artists = audio['TPE1'].text[0].split('/')
                    for artist in artists:
                        if artist not in data['artists']:
                            data['artists'][artist] = {'songs': [], 'fts': []}

                        if song not in data['artists'][artist]['songs']:
                            data['artists'][artist]['songs'].append(song)

                        data['artists'][artist]['fts'] = data['artists'][artist]['fts'] + list(set(artists) - set(data['artists'][artist]['fts']) - set([artist]))

                except KeyError:
                    print('Edit artists on {}'.format(song[:-4]))

    if save:    
        save_file(data)

    return data['artists']

_tree = generate_tree(DIRECTORY)

def get_artist_songs(artist):
    return _tree[artist]['songs']

def generate_songs_list(artists):
    global _dupe_artists
    songs_list = []

    if len(artists) < 2:
        return songs_list

    artist = artists[0]
    songs_list = get_artist_songs(artist)

    for next in artists[1:]:
        # Iterate through the artist paths between each artist.
        a_path = get_connecton(artist, next, _dupe_artists)
        _dupe_artists = _dupe_artists + a_path
        p = artist
        song = None
        
        # For each artist in the given path.
        for a in a_path:
            # Choose a song that is shared between the previous and next artist.
            shared_songs = get_shared_songs(p, a)
            song = choice(shared_songs)
            
            # Moves the song to the end of the list.
            if song in songs_list:
                songs_list.remove(song)
            songs_list.append(song)

            # Adds the rest of the songs from the next artist to the list.
            songs_list = songs_list + list(set(get_artist_songs(a)) - set(shared_songs) - set(songs_list))
            p = a
        
        # If there is no artist path between the two artists.
        if not a_path:
            print('No artists between {} and {}.'.format(artist, next))
            songs_list = songs_list + get_artist_songs(next)

        artist = next
    
    return songs_list

def get_shared_songs(artist1, artist2):
    return list(set(get_artist_songs(artist1)).intersection(get_artist_songs(artist2)))

def get_fts(artist):
    return _tree[artist]['fts']

# Returns a list of artists between the src and dst artist.
def get_connecton(src_artist, dst_artist, checked_artists):
    checked_artists.append(src_artist)
    
    if dst_artist in _tree[src_artist]['fts']:
        return [dst_artist]

    for ft in _tree[src_artist]['fts']:
        if ft not in checked_artists:
            # checked_artists.append(ft)
            path = get_connecton(ft, dst_artist, checked_artists)

            if path:
                return [ft] + path

    return []

def get_artists():
    return list(_tree.keys())
