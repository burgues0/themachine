import yt_dlp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from args import get_args
from concurrent.futures import ThreadPoolExecutor

def fetch_album_songs(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                song_urls = [entry['url'] for entry in info['entries']]
                album_name = info.get('title', 'Unknown Album').replace('Album - ', '').strip()
                filenames = []
                for entry in info['entries']:
                    artist = entry.get('artist', entry.get('uploader', 'Unknown'))
                    if isinstance(artist, list):
                        artist = artist[0]
                    artist = artist.split(',')[0].strip()
                    
                    title = entry.get('title', 'Unknown')
                    filenames.append(f"{artist} - {album_name} - {title}")
                return song_urls, filenames
            else:
                artist = info.get('artist', info.get('uploader', 'Unknown'))
                if isinstance(artist, list):
                    artist = artist[0]
                artist = artist.split(',')[0].strip()
                album = info.get('album', 'Unknown')
                title = info.get('title', 'Unknown')
                filename = f"{artist} - {album} - {title}"
                return [url], [filename]
        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")
            return [], []

def download_song(url, extension, bitrate, filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 3,
        'outtmpl': f'{filename}.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': extension,
                'preferredquality': bitrate,
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            },
        ],
        'postprocessor_args': {
            'ffmpeg': [
                '-vf', 'crop=ih:ih:(iw-ih)/2:0',
            ],
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Error downloading {url}: {e}")

def themachine():
    args = get_args()
    songs, filenames = fetch_album_songs(args.url)
    console = Console()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        tasks = {}
        for i, (url, filename) in enumerate(zip(songs, filenames)):
            task_id = progress.add_task(f"[red]{filename}", total=1)
            tasks[url] = (task_id, i)

        def download_with_progress(url):
            task_id, index = tasks[url]
            try:
                download_song(url, args.extension, args.bitrate, filenames[index])
                progress.update(task_id, completed=1, description=f"[green]{filenames[index]}")
            except Exception as e:
                progress.update(task_id, completed=1, description=f"[red]{filenames[index]} - Error")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(download_with_progress, url) for url in songs]
            for future in futures:
                future.result()
    
    return True