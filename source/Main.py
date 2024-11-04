import datetime
import logging
import itertools

from NETinterface import NETinterface
from OSinterface import OSinterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ignore my ignorant mixup of camel and snake case, im used to java my beloved

spotifyClient = NETinterface()

myUserID = ''
myPlaylistURI = spotifyClient.get_playlists(myUserID)['items'][0]['uri']
myLocalPlaylistPath = r''
myPlayTimePath = r''


def add_parallel(supplier, startIndex=0, endIndex=None, position=None):
    failed = []
    succeeded = []
    bulk = []
    for artist, song in itertools.islice(supplier, startIndex, endIndex):
        try:
            track_uri = spotifyClient.get_track(artist, song)['tracks']['items'][0]['uri']
            bulk.append(track_uri)
            if len(bulk) == 100:
                spotifyClient.add_tracks_to_playlist(myPlaylistURI, bulk, position)
                print("Adding 100 tracks to playlist.")
                bulk = []
            logging.info(f"Stored {artist} - {song}")
            succeeded.append((artist, song))
        except Exception as e:
            spotifyClient.add_tracks_to_playlist(myPlaylistURI, bulk, position)
            bulk = []
            failed.append((artist, song))
            logging.error(f"Failed to find {artist} - {song}: {e}")
            print(
                f"Failed to find {artist} - {song}. Please check the details, add manually and press 'y' to continue.")
            while True:
                user_input = input("Press 'y' to continue: ")
                if user_input.lower() == 'y':
                    break
    spotifyClient.add_tracks_to_playlist(myPlaylistURI, bulk, position)
    bulk = []
    logging.info(f"Failed to add {len(failed)} tracks.")
    print(failed)
    return succeeded, failed


def add_serial(supplier, startIndex=0, endIndex=None):
    failed = []
    succeeded = []
    for artist, song in itertools.islice(supplier, startIndex, endIndex):
        try:
            # Get the track uri
            track_uri = spotifyClient.get_track(artist, song)['tracks']['items'][0]['uri']
            # Add the track to the playlist
            spotifyClient.add_track_to_playlist(myPlaylistURI, track_uri)
            logging.info(f"Added {artist} - {song}")
            succeeded.append((artist, song))
        except Exception as e:
            failed.append((artist, song))
            logging.error(f"Failed to add {artist} - {song}: {e}")
            print(f"Failed to add {artist} - {song}. Please check the details and press 'y' to continue.")
            while True:
                user_input = input("Press 'y' to continue: ")
                if user_input.lower() == 'y':
                    break
    logging.info(f"Failed to add {len(failed)} tracks.")
    print(failed)
    return succeeded, failed


# Example use cases:------------------------------------------------------------------------------------------------

# count all songs per artist; returns a dictionary
artist_song_map = OSinterface.get_artist_song_map(myLocalPlaylistPath, sort_alphabetically=True)

# collect all locally stored songs; returns a generator / supplier of artist-song tuples
artist_song_tuples = OSinterface.get_artist_song_tuples(myLocalPlaylistPath, sort_alphabetically=True,
                                                        case_sensitive=False, ignore_brackets=True)

# add all songs to the playlist (avoid using the serial method, since itll get you 429 rate limited for larger
# playlists!) when encountering an error, the script will pause and ask you to press 'y' to continue, this is to give
# you the opportunity to fix add the song manually
succeeded, failed = add_parallel(artist_song_tuples)
# optionally you can log your change to the playlist
spotifyClient.log_playlist_changes(myPlaylistURI,
            description=f'Added {len(succeeded) - len(failed)} items on {datetime.datetime.now().strftime("%Y-%m-%d")}')

# read all songs from the playlist; the spotifyClient response is a json object that can be parsed with the
# spotifyClient.parse_artist_song method
#
#   to narrow down the data returned by the spotify api, you can specify the fields parameter in
#   the get_all_playlist_tracks method.
#   To achieve this successfully, you need to know the structure of the json object returned by the spotify api.
#   Therefore, I suggest you json dumping and linting the response
#   if you need different data fields, you can change the fields parameter to your liking, an empty parameter defaults
#   to all available fields
#   I created a template parse method, that assumes all fields are present, else they'll be filled with a placeholder
response = spotifyClient.get_all_playlist_tracks(myPlaylistURI, fields="items(track(name,artists(name))")
# print(json.dumps(response))
playlistContent = []  # only needed for the next example
listOfWhateverPythonJustCreatedForMe = spotifyClient.parse_artist_song(response)
for artists, song in listOfWhateverPythonJustCreatedForMe:
    if len(artists) > 1:
        print(f"{' & '.join(artists)} - {song}")
        playlistContent.append(f"{artists[0]} - {song}")  # only needed for the next example

    else:
        print(f"{artists[0]} - {song}")
        playlistContent.append(f"{artists[0]} - {song}")  # only needed for the next example

# lastly we can count the duplicates and print them
cleaned = playlistContent  # [song.replace("prefix for example - ", "") for song in list]
song_counts = {song: cleaned.count(song) for song in cleaned}
duplicates = {song: count for song, count in song_counts.items() if count > 1}
uniques = {song: count for song, count in song_counts.items() if count == 1}
for song, count in duplicates.items():
    print(f"{song} \t\t {count}")  # formatting sucks

# A list of the most listened songs (probably pretty unrepresentative of my taste in music since I listen on shuffle)
# That we can add to the top of the playlist
add_parallel(OSinterface.read_most_listened_file(myPlayTimePath, lines=25), position=0)
spotifyClient.log_playlist_changes(myPlaylistURI,
                                   description=f'Added the 25 most listened tracks to the top of the playlist')
