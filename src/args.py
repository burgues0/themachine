import argparse

def get_args():
    parser = argparse.ArgumentParser(prog='themachine', description='Another yt-dlp based script, focused on "searching" full albums with quality.')

    parser.add_argument('-u', '--url', required=True, help="Reference URL of choice.")
    parser.add_argument('-e', '--extension', choices=['mp3', 'flac', 'wav'], help="Determine the file extension of the output.")
    parser.add_argument('-b', '--bitrate', help="Determine the bitrate of the output.")
    parser.add_argument('-c', '--check', action='store_true', help="Check if the output matches the expected result.")
    
    return parser.parse_args()
