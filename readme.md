# Spotify Playlist Manager

This project is a Python-based application that interacts with the Spotify API to manage playlists. 
The Scripts act as an abstraction-layer to the API itself and it allows users to more easily add tracks from local files
to a Spotify playlist, log changes, and read playlist content.

## Features

The functionality in `OSinterface.py` assumes that the songs in the local directory are named after the following pattern:
`artist - songname.mp3`

To indicate that a variable used in a code block references an occurrence from an earlier code block, you can add a comment in the code block or a note in the README. Here is an example of how you can do it:

### Example Use Cases

#### Count All Songs per Artist

Count all songs per artist in a local directory and return a dictionary:
```python
artist_song_map = OSinterface.get_artist_song_map(myLocalPlaylistPath, sort_alphabetically=True)
print(artist_song_map)
```

#### Collect All Locally Stored Songs

Collect all locally stored songs and return a generator of artist-song tuples:
```python
artist_song_tuples = OSinterface.get_artist_song_tuples(myLocalPlaylistPath, sort_alphabetically=True, case_sensitive=False, ignore_brackets=True)
```

#### Add All Songs to the Playlist

Add all songs to the playlist using the parallel method to avoid rate limiting:
```python
# `artist_song_tuples` is defined in the "Collect All Locally Stored Songs" section
succeeded, failed = add_parallel(artist_song_tuples)
```

Optionally, log the changes made to the playlist:
```python
# `succeeded` and `failed` are defined in the "Add All Songs to the Playlist" section
spotifyClient.log_playlist_changes(myPlaylistURI, description=f'Added {len(succeeded) - len(failed)} items on {datetime.datetime.now().strftime("%Y-%m-%d")}')
```

#### Read All Songs from the Playlist

Read all songs from the playlist and parse the response:
```python
response = spotifyClient.get_all_playlist_tracks(myPlaylistURI, fields="items(track(name,artists(name))")
playlistContent = spotifyClient.parse_artist_song(response)
for artists, song in playlistContent:
    if len(artists) > 1:
        print(f"{' & '.join(artists)} - {song}")
    else:
        print(f"{artists[0]} - {song}")
```

#### Count and Print Duplicates

Count and print duplicate songs in the playlist:
```python
# `playlistContent` is defined in the "Read All Songs from the Playlist" section
cleaned = playlistContent
song_counts = {song: cleaned.count(song) for song in cleaned}
duplicates = {song: count for song, count in song_counts.items() if count > 1}
for song, count in duplicates.items():
    print(f"{song} \t\t {count}")
```

#### Add Most Listened Songs to the Top of the Playlist

Add the most listened songs to the top of the playlist:
```python
add_parallel(OSinterface.read_most_listened_file(myPlayTimePath, lines=25), position=0)
spotifyClient.log_playlist_changes(myPlaylistURI, description=f'Added the 25 most listened tracks to the top of the playlist')
```
>[!NOTE]
> The `read_most_listened_file` function reads the first lines of a plain-text file with path `myPlayTimePath` that contains the songs, in my case sorted by descending play count.
> The expected format is `artist - songname`, brackets of any kind are ignored.

## Requirements

- Python 3.x
- `spotipy` library
- `dotenv` library
- Spotify Developer Account

## Installation

1. Clone the repository:
    ```shell
    git clone https://github.com/grn-x/Python-Playlist-Digitization.git
    cd spotify-playlist-manager
    ```

2. Install the required Python packages:
    ```shell
    pip install -r requirements.txt
    ```

3. Set up your Spotify API credentials in the `source/credentials.env` file:
    ```dotenv
    SPOTIPY_CLIENT_ID='your_client_id'
    SPOTIPY_CLIENT_SECRET='your_client_secret'
    SPOTIPY_REDIRECT_URI='http://127.0.0.1:9090'
    ```

## Usage

The `main.py` script contains usage examples for the different features of the application. Run the script to see the examples:
 

## Technical Details:

The project is divided into different scripts that interface with various components

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE.md) file for details.
