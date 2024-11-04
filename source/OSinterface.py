import os
import re
from collections import defaultdict


class OSinterface:
    @staticmethod
    def get_artist_song_map(folder_path, sort_alphabetically=True):
        artist_song_count = defaultdict(int)

        for filename in os.listdir(folder_path):
            if filename.endswith('.mp3') and '-' in filename:
                artist, song_title = map(str.strip, filename.rsplit('-', 1))
                # song_title = song_title[:-4]  # Strip the .mp3 extension
                artist_song_count[artist] += 1

        if sort_alphabetically:
            artist_song_count = dict(sorted(artist_song_count.items()))
        else:
            artist_song_count = dict(sorted(artist_song_count.items(), key=lambda item: item[1], reverse=True))

        return artist_song_count

    @classmethod
    def get_artist_songs(cls, folder_path, sort_alphabetically=True, case_sensitive=True, ignore_brackets=False):
        artist_song_map = defaultdict(list)

        for filename in os.listdir(folder_path):
            if filename.endswith('.mp3') and '-' in filename:
                if ignore_brackets:
                    filename = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}|\<.*?\>', '',
                                      filename).strip()  # \[.*?\]|\(.*?\) I fucking hate regex but its so beautiful
                    if filename == '' or filename == '.mp3':
                        continue
                artist, song_title = map(str.strip, filename.rsplit('-', 1))
                song_title = song_title[:-4]  # Strip the .mp3 extension
                if not case_sensitive:
                    artist = artist.lower()
                artist_song_map[artist].append(song_title)

        if sort_alphabetically:
            artist_song_map = dict(
                sorted(artist_song_map.items(), key=lambda item: item[0] if case_sensitive else item[0].lower()))
        else:
            artist_song_map = dict(sorted(artist_song_map.items(), key=lambda item: len(item[1]), reverse=True))

        return artist_song_map

    @staticmethod
    def get_artist_song_tuples(folder_path, sort_alphabetically=True, case_sensitive=True, ignore_brackets=False):
        artist_songs = OSinterface.get_artist_songs(folder_path, sort_alphabetically, case_sensitive, ignore_brackets)
        for artist, songs in artist_songs.items():
            for song in songs:
                yield artist, song

    @staticmethod
    def read_most_listened_file(path, lines=50):
        with open(path, 'r') as file:
            file_lines = file.readlines()
        for string in file_lines[:lines]:
            clean_string = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}|\<.*?\>', '', string).strip()
            artist, song = map(str.strip, clean_string.rsplit('-', 1))
            yield artist, song
