import yt_dlp
from args import get_args
from tqdm import tqdm
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
            else:
                return url

        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")

def download_song(url, extension, bitrate):

    # TO-DO!! NOT WORKING
    # pbar = None
    # def progress_hook(d):
    #     nonlocal pbar
    #     if d['status'] == 'downloading':
    #         if pbar is None:
    #             pbar = tqdm(total=d.get('total_bytes'), unit='B', unit_scale=True, desc=d['filename'][:20])
    #         pbar.update(d.get('downloaded_bytes', 0) - pbar.n)
    #     elif d['status'] == 'finished':
    #         if pbar: pbar.close()

    # TO-DO - IMAGE IS NOT PROPERLY CROPPED & ARTIST IS RETURNING LONG LIST

    ydl_opts = {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': extension,
                'preferredquality': bitrate,
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
                'when': 'before_dl',
            },
            {
                'key': 'EmbedThumbnail'
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True
            },
        ],
        # 'progress_hooks': [progress_hook],
        'outtmpl': '%(uploader)s - %(title)s.%(ext)s',
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

    songs = fetch_album_songs(args.url)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(download_song(args.url, args.extension, args.bitrate), songs)

    return True