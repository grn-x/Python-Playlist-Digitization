# Spotify Playlist Manager

This project is a Python-based application that interacts with the Spotify API to manage playlists. It allows users to add tracks from local files to a Spotify playlist, log changes, and read playlist content.

## Features


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
