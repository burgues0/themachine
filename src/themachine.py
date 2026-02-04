import json
import yt_dlp
from args import get_args
from concurrent.futures import ThreadPoolExecutor

def fetch_song_data():
    return True

def fetch_album_songs(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                song_urls = [entry['url'] for entry in info['entries']]
                return song_urls

        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")

def download_song(url, extension, bitrate):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': extension,
            'preferredquality': bitrate,
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Starting: {url}")
            ydl.download([url])
            print(f"Finished: {url}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")


def themachine():
    args = get_args()

    songs = fetch_album(args.url)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(download_song(args.url, args.extension, args.bitrate), songs)

    return True