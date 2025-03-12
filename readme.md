# Spotify Playlist Manager

A Python-based application that interacts with the Spotify API to manage playlists. 
The contained scripts act as an abstraction-layer to the API itself to allow for easier playlist management.

## Features
>[!IMPORTANT]
> The functionality in `OSinterface.py` assumes that the songs in the local directory are named after the following pattern: 
> `artist - songname.mp3`


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

<details>
<summary>
Add all songs to the playlist using the parallel method to avoid rate limiting (that could otherwise occur when using the sequential method):
</summary>
The method will first loop through the provided generator of artist-song tuples and search for the track on Spotify.
The returned track ID will be stashed in a list and added if the maximum batch size of 100 is reached, or an exception is raised.

> [!TIP]
> Should the API fail to find the searched track, all currently cached tracks will be added, and execution will pause until
> confirmation is provided via the console. This is to allow for manually adding the missing track to maintain the playlist order


</details>


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
> This file is generated by an external software. The expected format is `artist - songname`, brackets of any kind are ignored.

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
>[!NOTE]
> To obtain your Spotify API credentials, create a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
> Refer to the [Spotify web-API docs](https://developer.spotify.com/documentation/web-api) for more information.


4. Run the `main.py` script or use isolated features in your own scripts:
    ```shell
    python main.py
    ```

## Usage

The `main.py` script contains usage examples for the different features of the application. Run the script to see the examples:
 

## Roadmap
- [x] Add Tracks by their OS filename
- [x] Search for duplicates
- [x] Handle track not found exceptions
    - [ ] Add option to auto skip missing tracks 
- [ ] Implement Metadata Extraction
  - [ ] chain to ID3v2 tagging


## Help & Contributing

If you have any questions or suggestions, feel free to open an issue or a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE.md) file for details.
