import argparse

def get_args():
    parser = argparse.ArgumentParser(prog='themachine', description='Another yt-dlp based script, focused on "searching" full albums.')

    parser.add_argument('-u', '--url', required=True, help="reference URL of choice.")
    parser.add_argument('-e', '--extension', choices=['mp3', 'flac', 'wav'], default='flac', help="determine the file extension of the output.")
    parser.add_argument('-b', '--bitrate', default='128', help="determine the bitrate of the output.")
    parser.add_argument('-c', '--check', action='store_true', help="check if the output matches the expected result.")
    parser.add_argument('-y', action='store_true', help="skip verification before downloading")
    parser.add_argument('--artist', default=None, help="overrides the folder and filename of the output with the informed value.")
    parser.add_argument('--album', default=None, help="overrides the album of the output with the informed value.")
    parser.add_argument('--year', default=None, help="overrides the release year for a specific album/song.")
    parser.add_argument('--genre', default=None, help="overrides the genre for a specific album/song.")
    parser.add_argument('--title', default=None, help="overrides the title for a specific album/song.")
    
    return parser.parse_args()
