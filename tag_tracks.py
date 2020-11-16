import spotify
import tagger
from re import findall, sub
from os import listdir
import argparse

# parses arguments
parser = argparse.ArgumentParser()
parser.add_argument('path' , help='path to playlist directory')
parser.add_argument('pattern', help='e.g. "Ric Flair Drip - Offset.m4a" would have the pattern "$track - $artist.m4a"')
args = parser.parse_args()

# gets extension of file
ext = lambda path: path.split('.')[-1]
path = args.path
pattern = args.pattern
parent_dir = '/'.join(path.split('/')[:-1])
files = listdir(path)

for file in files:
    # checks if the file is just artwork
    if ext(file) == 'jpg':
        continue

    # finds info using pattern and filename
    # returns dict: {'track': 'Back in the U.S.S.R', 'album': 'The Beatles'...}
    info = tagger.parse_filenames(pattern, file)
    # I only use the 'track' and 'artist' here
    r = spotify.search_track(tagger.format(info['track'] + ' ' + info['artist']))
    # search_track returns None if there are no results
    if r:
        r['path'] = f'{parent_dir}/{file}'
        # WILL NOT WORK without setting a value for the 'path' key
        tagger.set_track_tags(r)
    else:
        print(file, ' not found.')
