import os
import yt_dlp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from args import get_args
from concurrent.futures import ThreadPoolExecutor
from mutagen.flac import FLAC
from pathlib import Path

def extract_first_artist(artist_field):
    if not artist_field or artist_field == 'Unknown':
        return 'Unknown'
    if isinstance(artist_field, list):
        artist_field = artist_field[0] if artist_field else 'Unknown'
    if artist_field and artist_field != 'Unknown':
        return artist_field.split(',')[0].strip()
    return 'Unknown'

def create_metadata_dict(artist, album, title, track, total_tracks, year, album_artist, genre, song_url, disc='1', composer='', copyright=''):
    return {
        'artist': artist,
        'album': album,
        'title': title,
        'track': track,
        'totaltracks': total_tracks,
        'date': year,
        'albumartist': album_artist,
        'genre': genre,
        'comment': song_url,
        'composer': composer,
        'copyright': copyright,
        'url': song_url,
        'encoded_by': 'yt-dlp',
        'disc': disc,
    }

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
                if not entries:
                    print("Error: Empty playlist")
                    return [], [], []

                song_urls = [entry['url'] for entry in entries]
                album_name = info.get('title', 'Unknown Album').replace('Album - ', '').strip()
                total_tracks = len(entries)

                with yt_dlp.YoutubeDL(ydl_opts_full) as ydl_full:
                    first_song_full = ydl_full.extract_info(entries[0]['url'], download=False)
                    album_artist = extract_first_artist(first_song_full.get('artist') or first_song_full.get('uploader'))
                    album_year = str(first_song_full.get('release_year', ''))
                    album_genre = first_song_full.get('genre', 'Music')

                base_dir = Path.home() / 'Music' / 'themachine' / album_artist / album_name
                base_dir.mkdir(parents=True, exist_ok=True)

                filenames = []
                metadata_list = []

                for i, entry in enumerate(entries):
                    artist = extract_first_artist(entry.get('channel'))
                    title = entry.get('title', 'Unknown')

                    filename_only = f"{artist} - {album_name} - {title}"
                    full_path = base_dir / filename_only
                    filenames.append(str(full_path))

                    track_num = str(i + 1)
                    song_url = f"https://music.youtube.com/watch?v={entry.get('id', '')}"
                    
                    metadata = create_metadata_dict(
                        artist=artist,
                        album=album_name,
                        title=title,
                        track=track_num,
                        total_tracks=str(total_tracks),
                        year=str(album_year),
                        album_artist=album_artist,
                        genre=album_genre,
                        song_url=song_url,
                        disc='1'
                    )
                    metadata_list.append(metadata)
                
                return song_urls, filenames, metadata_list
            else:
                artist = extract_first_artist(info.get('artist') or info.get('uploader'))
                album = info.get('album', 'Unknown')
                title = info.get('title', 'Unknown')
                
                base_dir = Path.home() / 'Music' / 'themachine' / artist / album
                base_dir.mkdir(parents=True, exist_ok=True)
                
                filename_only = f"{artist} - {album} - {title}"
                full_path = base_dir / filename_only
                song_url = f"https://music.youtube.com/watch?v={info.get('id', '')}"
                
                metadata = create_metadata_dict(
                    artist=artist,
                    album=album,
                    title=title,
                    track='1',
                    total_tracks='1',
                    year=str(info.get('release_year', '')),
                    album_artist=artist,
                    genre=info.get('genre', 'Music'),
                    song_url=song_url,
                    composer=info.get('composer', ''),
                    copyright=info.get('license', '')
                )
                
                return [url], [str(full_path)], [metadata]
        except Exception as e:
            print(f"Error extracting album/playlist info: {e}")
            return [], [], []

def add_metadata(filepath, metadata, extension):
    try:
        if extension != 'flac':
            raise NotImplementedError(f"Metadata for .{extension} format not implemented yet")
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
            display_name = Path(filename).name
            task_id = progress.add_task(f"[red]{display_name}", total=1)
            tasks[url] = (task_id, i)

        def download_with_progress(url):
            task_id, index = tasks[url]
            display_name = Path(filenames[index]).name
            try:
                download_song(url, args.extension, args.bitrate, filenames[index], metadata_list[index])
                progress.update(task_id, completed=1, description=f"[green]{display_name}")
            except Exception as e:
                progress.update(task_id, completed=1, description=f"[red]{display_name} - Error")

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(download_with_progress, url) for url in songs]
            for future in futures:
                future.result()
    
    return True