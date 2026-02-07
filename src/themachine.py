import yt_dlp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from args import get_args
from concurrent.futures import ThreadPoolExecutor

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
                filenames = [f"{entry.get('channel', 'Unknown')} - {entry.get('title', 'Unknown')}" 
                            for entry in info['entries']]
                return song_urls, filenames
            else:
                filename = f"{info.get('channel', 'Unknown')} - {info.get('title', 'Unknown')}"
                return [url], [filename]
        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")
            return [], []

def download_song(url, extension, bitrate):
    ydl_opts = {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 3,
        'outtmpl': '%(channel)s - %(title)s.%(ext)s',
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
                '-write_xing', '0'
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
        tasks = {url: progress.add_task(f"[red]{filename}", total=1) 
                 for url, filename in zip(songs, filenames)}
        
        def download_with_progress(url):
            try:
                download_song(url, args.extension, args.bitrate)
                progress.update(tasks[url], completed=1, description=f"[green]{filenames[songs.index(url)]}")
            except Exception as e:
                progress.update(tasks[url], completed=1, description=f"[red]{filenames[songs.index(url)]} - Error")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(download_with_progress, url) for url in songs]
            for future in futures:
                future.result()
    
    return True