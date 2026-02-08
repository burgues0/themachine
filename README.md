# themachine
Basic yt-dlp wrapper focused on downloading full albums in .flac format.

# Why?
The idea started because I was having some problems with SpotDL, where it was not as consistent as I wished for some artists, and frequently selected the wrong song versions (i.e.: wanted song X [explicit], got song X [censored]).

This wrapper is not even close in functionality to SpotDL (or any other download wrapper out there), it was created only for my specific needs, and what would work for me on the subject "Downloading songs for my personal music library."

Obs.: only tested with YT Music, for now.

# Usage

python main.py [args]

## Arguments

**-h** | **--help**: show the help message and exit

**-u** | **--url**: reference URL of choice.

**-e** | **--extension**: determine the file extension of the output.

**-b** | **--bitrate**: determine the bitrate of the output.

**-c** | **--check**: check if the output matches the expected result.

### Example

```
$ python main.py --help

usage: themachine [-h] -u URL [-e {mp3,flac,wav}] [-b BITRATE] [-c]

Another yt-dlp based script, focused on "searching" full albums with quality.

options:
  -h, --help            show this help message and exit
  -u, --url URL         reference URL of choice.
  -e, --extension {mp3,flac,wav}
                        determine the file extension of the output.
  -b, --bitrate BITRATE
                        determine the bitrate of the output.
  -c, --check           check if the output matches the expected result.
```

# Disclaimer
Before actually using the tool, you should support the original artists in some way or another. It's really hard to create art without financial support, specially for small artists. Buy an album or another in Bandcamp, buy some original merch, a vinyl, CD, any collectible etc. This way, you can help your favorite artists in creating music for your enjoyment.