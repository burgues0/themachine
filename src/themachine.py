import yt_dlp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from args import get_args
from concurrent.futures import ThreadPoolExecutor
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK
import os

def fetch_album_songs(url):
    ydl_opts_flat = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist'
    }
    ydl_opts_full = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                entries = [e for e in info['entries'] if e is not None]
                song_urls = [entry['url'] for entry in entries]
                album_name = info.get('title', 'Unknown Album').replace('Album - ', '').strip()
                total_tracks = len(entries)
                with yt_dlp.YoutubeDL(ydl_opts_full) as ydl_full:
                    first_song_full = ydl_full.extract_info(entries[0]['url'], download=False)
                    album_artist = first_song_full.get('artist') or first_song_full.get('uploader', 'Unknown')
                    if isinstance(album_artist, list):
                        album_artist = album_artist[0] if album_artist else 'Unknown'
                    if album_artist and album_artist != 'Unknown':
                        album_artist = album_artist.split(',')[0].strip()
                    
                    album_year = str(first_song_full.get('release_year', ''))
                    album_genre = first_song_full.get('genre', 'Music')
                
                filenames = []
                metadata_list = []
                
                for i, entry in enumerate(entries):
                    artist = entry.get('channel') or 'Unknown'
                    if artist and artist != 'Unknown':
                        artist = artist.split(',')[0].strip()
                    
                    title = entry.get('title', 'Unknown')
                    filenames.append(f"{artist} - {album_name} - {title}")
                    
                    track_num = str(i + 1)
                    song_url = f"https://music.youtube.com/watch?v={entry.get('id', '')}"
                    
                    metadata_list.append({
                        'artist': artist,
                        'album': album_name,
                        'title': title,
                        'track': track_num,
                        'totaltracks': str(total_tracks),
                        'date': album_year,
                        'albumartist': album_artist,
                        'genre': album_genre,
                        'comment': song_url,
                        'composer': '',
                        'copyright': '',
                        'url': song_url,
                        'encoded_by': 'yt-dlp',
                        'disc': '1',
                    })
                
                return song_urls, filenames, metadata_list
            else:
                artist = info.get('artist') or info.get('uploader') or 'Unknown'
                if isinstance(artist, list):
                    artist = artist[0] if artist else 'Unknown'
                if artist and artist != 'Unknown':
                    artist = artist.split(',')[0].strip()
                
                album = info.get('album', 'Unknown')
                title = info.get('title', 'Unknown')
                filename = f"{artist} - {album} - {title}"
                song_url = f"https://music.youtube.com/watch?v={info.get('id', '')}"
                
                metadata = {
                    'artist': artist,
                    'album': album,
                    'title': title,
                    'track': '1',
                    'totaltracks': '1',
                    'date': str(info.get('release_year', '')),
                    'albumartist': artist,
                    'genre': info.get('genre', 'Music'),
                    'comment': song_url,
                    'composer': info.get('composer', ''),
                    'copyright': info.get('license', ''),
                    'url': song_url,
                    'encoded_by': 'yt-dlp',
                    'disc': '1',
                }
                
                return [url], [filename], [metadata]
        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")
            return [], [], []

def add_metadata(filepath, metadata, extension):
    try:
        if extension == 'flac':
            audio = FLAC(filepath)
            audio['TITLE'] = metadata['title']
            audio['ARTIST'] = metadata['artist']
            audio['ALBUM'] = metadata['album']
            audio['ALBUMARTIST'] = metadata['albumartist']
            audio['TRACKNUMBER'] = metadata['track']
            audio['TRACKTOTAL'] = metadata['totaltracks']
            audio['DISCNUMBER'] = metadata['disc']
            audio['GENRE'] = metadata['genre']
            audio['COMMENT'] = metadata['comment']
            audio['URL'] = metadata['url']
            audio['ENCODED-BY'] = metadata['encoded_by']
            if metadata['date']:
                audio['DATE'] = metadata['date']
            if metadata['composer']:
                audio['COMPOSER'] = metadata['composer']
            if metadata['copyright']:
                audio['COPYRIGHT'] = metadata['copyright']
            audio.save()
    except Exception as e:
        print(f"Error adding metadata to {filepath}: {e}")

def download_song(url, extension, bitrate, filename, metadata):
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
            filepath = f"{filename}.{extension}"
            if os.path.exists(filepath):
                add_metadata(filepath, metadata, extension)
        except Exception as e:
            print(f"Error downloading {url}: {e}")

def themachine():
    args = get_args()
    songs, filenames, metadata_list = fetch_album_songs(args.url)
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
                download_song(url, args.extension, args.bitrate, filenames[index], metadata_list[index])
                progress.update(task_id, completed=1, description=f"[green]{filenames[index]}")
            except Exception as e:
                progress.update(task_id, completed=1, description=f"[red]{filenames[index]} - Error")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(download_with_progress, url) for url in songs]
            for future in futures:
                future.result()
    
    return True