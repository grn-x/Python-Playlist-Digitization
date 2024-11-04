import datetime
import json
import os
import pathlib
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging


class NETinterface:
    def __init__(self):
        envPath = pathlib.Path(r"credentials.env")
        load_dotenv(dotenv_path=envPath)

        self.SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
        self.SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
        self.SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

        self.auth_manager = SpotifyOAuth(
            client_id=self.SPOTIPY_CLIENT_ID,
            client_secret=self.SPOTIPY_CLIENT_SECRET,
            redirect_uri=self.SPOTIPY_REDIRECT_URI,
            scope="playlist-modify-public playlist-modify-private"
        )
        self.token_info = self.auth_manager.get_access_token(as_dict=True)
        self.sp = spotipy.Spotify(auth=self.token_info['access_token'])
        logging.info("Spotify client initialized with access token.")

    def refresh_token_if_needed(self):
        if self.auth_manager.is_token_expired(self.token_info):
            logging.info("Token expired, refreshing...")
            self.token_info = self.auth_manager.refresh_access_token(self.token_info['refresh_token'])
            self.sp = spotipy.Spotify(auth=self.token_info['access_token'])
            logging.info("Token refreshed.")

    def get_playlists(self, user_id):
        self.refresh_token_if_needed()
        return self.sp.user_playlists(user_id)

    def get_track(self, artistName, trackName):
        self.refresh_token_if_needed()
        return self.sp.search(q=f'artist:{artistName} track:{trackName}', type='track')

    def add_track_to_playlist(self, playlist_id, track_uri):
        self.refresh_token_if_needed()
        return self.sp.playlist_add_items(playlist_id, [track_uri])

    def append_tracks_to_playlist(self, playlist_id, track_uris):
        if len(track_uris) == 0:
            logging.error("No tracks to add.")
            return
        self.refresh_token_if_needed()
        logging.info(f"Adding {len(track_uris)} tracks to playlist.")
        return self.sp.playlist_add_items(playlist_id, track_uris)

    def add_tracks_to_playlist(self, playlist_id, track_uris, position=None):
        if position is None:
            return self.append_tracks_to_playlist(playlist_id, track_uris)
        if len(track_uris) == 0:
            logging.error("No tracks to add.")
            return
        self.refresh_token_if_needed()
        range_start = self.get_playlist_length(playlist_id)
        logging.info(f"Adding {len(track_uris)} tracks to playlist.")
        self.sp.playlist_add_items(playlist_id, track_uris)
        return self.sp.playlist_reorder_items(playlist_id, range_start=range_start, range_length=len(track_uris), insert_before=position)

    def get_playlist_description(self, playlist_id):
        self.refresh_token_if_needed()
        playlist = self.sp.playlist(playlist_id)
        return playlist['description']

    def set_playlist_description(self, playlist_id, description):
        self.refresh_token_if_needed()
        return self.sp.playlist_change_details(playlist_id, description=description)

    def log_playlist_changes(self, playlist_id, description=None):
        prefix = f' --- //{self.__class__.__name__}.py: '
        suffix = '//'
        if description is None:
            description = f'Changed on {datetime.datetime.now().strftime("%Y-%m-%d")}'
        return self.set_playlist_description(playlist_id,  self.get_playlist_description(playlist_id) + prefix + description + suffix)

    def get_playlist_length(self, playlist_id):
        self.refresh_token_if_needed()
        playlist_details = self.sp.playlist(playlist_id, fields="tracks.total")
        return playlist_details['tracks']['total']

    def get_raw_json_playlist_tracks(self, playlist_id, offset=0, bulk_size=2):
        self.refresh_token_if_needed()
        return json.dumps(self.sp.playlist_items(playlist_id, offset=offset, limit=bulk_size))

    def __get_playlist_tracks__(self, playlist_id, offset=0, bulk_size=100, fields=None):
        self.refresh_token_if_needed()
        return self.sp.playlist_items(playlist_id, offset=offset, limit=bulk_size, fields=fields)

    def get_all_playlist_tracks(self, playlist_id, fields=None, limit=None, offset=0, bulk_size=100):
        tracks = []
        if limit is not None and limit < bulk_size:
            bulk_size = limit
        if limit is None:
            while offset < self.get_playlist_length(playlist_id):
                response = self.__get_playlist_tracks__(playlist_id, offset=offset, fields=fields, bulk_size=bulk_size)
                offset += bulk_size
                logging.info(f"Retrieved {len(response['items'])} tracks." + str(response['items']))
                tracks.extend(response['items'])
        else:
            iterations = limit // bulk_size
            rest = limit % bulk_size
            for i in range(iterations):
                response = self.__get_playlist_tracks__(playlist_id, offset=offset, fields=fields, bulk_size=bulk_size)
                offset += bulk_size
                logging.info(f"Retrieved {len(response['items'])} tracks." + str(response['items']))
                tracks.extend(response['items'])
            if rest > 0:
                response = self.__get_playlist_tracks__(playlist_id, offset=offset, fields=fields, bulk_size=rest)
                logging.info(f"Retrieved {len(response['items'])} tracks." + str(response['items']))
                tracks.extend(response['items'])
        return tracks

    def extract_track_info(self, tracks, selected_fields):
        track_info = {}
        for item in tracks:
            track = item['track']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            key = (track_name, artist_name)
            value = {field: track.get(field, None) for field in selected_fields}
            track_info[key] = value
        return track_info

    @staticmethod
    def print_parsed_response_template(self, response):
        empty = "N/A"
        for index, track_info in enumerate(response):
            print(f"Track {index + 1} details:")

            # Extracting first-level fields
            added_at = track_info.get("added_at", empty)
            added_by = track_info.get("added_by", {}).get("id", empty)
            is_local = track_info.get("is_local", False)
            primary_color = track_info.get("primary_color", empty)

            # Track details
            track = track_info.get("track", {})
            track_name = track.get("name", empty)
            track_id = track.get("id", empty)
            track_uri = track.get("uri", empty)
            duration_ms = track.get("duration_ms", 0)
            explicit = track.get("explicit", False)
            preview_url = track.get("preview_url", empty)
            popularity = track.get("popularity", empty)
            track_url = track.get("external_urls", {}).get("spotify", empty)
            track_markets = track.get("available_markets", [])

            # Album details
            album = track.get("album", {})
            album_name = album.get("name", empty)
            album_id = album.get("id", empty)
            album_uri = album.get("uri", empty)
            release_date = album.get("release_date", empty)
            release_precision = album.get("release_date_precision", empty)
            album_type = album.get("album_type", empty)
            album_markets = album.get("available_markets", [])
            album_url = album.get("external_urls", {}).get("spotify", empty)

            # Album images
            album_images = album.get("images", [])
            image_urls = [image.get("url", empty) for image in album_images]

            # Album artists
            album_artists = album.get("artists", [])
            album_artist_details = [
                {
                    "name": artist.get("name", empty),
                    "id": artist.get("id", empty),
                    "uri": artist.get("uri", empty),
                    "url": artist.get("external_urls", {}).get("spotify", empty)
                }
                for artist in album_artists
            ]

            # Track artists
            track_artists = track.get("artists", [])
            track_artist_details = [
                {
                    "name": artist.get("name", empty),
                    "id": artist.get("id", empty),
                    "uri": artist.get("uri", empty),
                    "url": artist.get("external_urls", {}).get("spotify", empty)
                }
                for artist in track_artists
            ]

            # External IDs
            external_ids = track.get("external_ids", {})
            isrc = external_ids.get("isrc", empty)

            # Video thumbnail
            video_thumbnail_url = track_info.get("video_thumbnail", {}).get("url", empty)

            # Print all details
            print(f"  Added At: {added_at}")
            print(f"  Added By: {added_by}")
            print(f"  Is Local: {is_local}")
            print(f"  Primary Color: {primary_color}")
            print(f"  Track Name: {track_name}")
            print(f"  Track ID: {track_id}")
            print(f"  Track URI: {track_uri}")
            print(f"  Duration (ms): {duration_ms}")
            print(f"  Explicit: {explicit}")
            print(f"  Preview URL: {preview_url}")
            print(f"  Popularity: {popularity}")
            print(f"  Track URL: {track_url}")
            print(f"  Track Available Markets: {', '.join(track_markets)}")

            print("\n  Album Details:")
            print(f"    Album Name: {album_name}")
            print(f"    Album ID: {album_id}")
            print(f"    Album URI: {album_uri}")
            print(f"    Release Date: {release_date}")
            print(f"    Release Precision: {release_precision}")
            print(f"    Album Type: {album_type}")
            print(f"    Album URL: {album_url}")
            print(f"    Album Available Markets: {', '.join(album_markets)}")
            print(f"    Album Images: {', '.join(image_urls)}")

            print("\n  Album Artists:")
            for artist in album_artist_details:
                print(f"    - Name: {artist['name']}, ID: {artist['id']}, URI: {artist['uri']}, URL: {artist['url']}")

            print("\n  Track Artists:")
            for artist in track_artist_details:
                print(f"    - Name: {artist['name']}, ID: {artist['id']}, URI: {artist['uri']}, URL: {artist['url']}")

            print(f"  ISRC: {isrc}")
            print(f"  Video Thumbnail URL: {video_thumbnail_url}")

            print("\n" + "=" * 40 + "\n")

    @staticmethod
    def parse_artist_song(response):
        returns = []
        empty = "N/A"
        for index, track_info in enumerate(response):
            # Track details
            track = track_info.get("track", {})
            track_name = track.get("name", empty)

            # Track artists
            artists = []
            track_artists = track.get("artists", [])
            track_artist_details = [
                {
                    "name": artist.get("name", empty),

                }
                for artist in track_artists
            ]
            for artist in track_artist_details:
                artists.append(artist['name'])
            returns.append((artists, track_name))

        return returns

