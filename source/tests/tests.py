import unittest
import os
import pathlib
from unittest.mock import mock_open, patch
from dotenv import load_dotenv
from source.OSinterface import OSinterface


# useless test class to boost the project impressions 😇

class TestOSinterface(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and files for testing
        self.test_dir = 'test_music'
        os.makedirs(self.test_dir, exist_ok=True)
        self.files = [
            'Artist1 - Song1.mp3',
            'Artist2 - Song2.mp3',
            'Artist1 - Song3.mp3',
            'Artist3 - Song4.mp3',
            'Artist2 - Song5.mp3',
            'Artist3 - Song6 (Live).mp3',
            'Artist4 - Song7.mp3'
        ]
        for file in self.files:
            open(os.path.join(self.test_dir, file), 'a').close()

        # Create the test file for the test_test_method
        self.test_file_path = os.path.join(self.test_dir, 'test_file.txt')
        mock_file_content = "artist5 - song1\nartist7 - song2\nartist5 - song3\n"
        with open(self.test_file_path, 'w') as f:
            f.write(mock_file_content)

    def tearDown(self):
        # Remove the temporary directory and files after testing
        for file in self.files:
            os.remove(os.path.join(self.test_dir, file))
        os.remove(self.test_file_path)
        os.rmdir(self.test_dir)


    def test_get_artist_song_map(self):
        result = OSinterface.get_artist_song_map(self.test_dir, sort_alphabetically=True)
        expected = {
            'Artist1': 2,
            'Artist2': 2,
            'Artist3': 2,
            'Artist4': 1
        }
        self.assertEqual(result, expected)

    def test_get_artist_songs(self):
        result = OSinterface.get_artist_songs(self.test_dir, sort_alphabetically=True, case_sensitive=False,
                                              ignore_brackets=True)
        expected = {
            'artist1': ['Song1', 'Song3'],
            'artist2': ['Song2', 'Song5'],
            'artist3': ['Song4', 'Song6 '],
            'artist4': ['Song7']
        }
        self.assertEqual(result, expected)

    def test_get_artist_song_tuples(self):
        result = list(OSinterface.get_artist_song_tuples(self.test_dir, sort_alphabetically=True, case_sensitive=False,
                                                         ignore_brackets=True))
        expected = [
            ('artist1', 'Song1'),
            ('artist1', 'Song3'),
            ('artist2', 'Song2'),
            ('artist2', 'Song5'),
            ('artist3', 'Song4'),
            ('artist3', 'Song6 '),
            ('artist4', 'Song7')
        ]
        self.assertEqual(result, expected)

    def test_test_method(self):
        expected_output = [
            ('artist5', 'song1'),
            ('artist7', 'song2'),
            ('artist5', 'song3')
        ]
        result = list(OSinterface.test(self.test_file_path, lines=3))
        self.assertEqual(result, expected_output)

    def test_env_variables(self):
        envPath = pathlib.Path(__file__).resolve().parent.parent / 'credentials.env'
        load_dotenv(dotenv_path=envPath)

        SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
        SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
        SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

        self.assertIsNotNone(SPOTIPY_REDIRECT_URI, "SPOTIPY_REDIRECT_URI is None")
        self.assertIsNotNone(SPOTIPY_CLIENT_ID, "SPOTIPY_CLIENT_ID is None")
        self.assertIsNotNone(SPOTIPY_CLIENT_SECRET, "SPOTIPY_CLIENT_SECRET is None")

        self.assertIsInstance(SPOTIPY_REDIRECT_URI, str, "SPOTIPY_REDIRECT_URI is not a string")
        self.assertIsInstance(SPOTIPY_CLIENT_ID, str, "SPOTIPY_CLIENT_ID is not a string")
        self.assertIsInstance(SPOTIPY_CLIENT_SECRET, str, "SPOTIPY_CLIENT_SECRET is not a string")


if __name__ == '__main__':
    unittest.main()
