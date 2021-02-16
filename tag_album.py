import re
import argparse
import os
from tqdm import tqdm
from pathlib import Path

import spotify
import discogs

def match(album, dir, pattern, quiet=False):
    for file in find('flac', 'm4a', dir=dir):
        for track in album:
            if track.matches(file, pattern=pattern):
                if not quiet:
                    print(colorize(track['title'], 1), end='')
                    print(' \u2192 ', end='')
                    print(file.split('/')[-1])


    for track in album:
        if track['filepath'] is None and not quiet:
            print(colorize(track['title'], 0), end='')
            print(' \u2192 ', end='')
            print('?')


def tag_all(album, quiet=False):
    if quiet:
        iter = album
    else:
        iter = tqdm(album, unit='tracks')
    for track in iter:
        if track['filepath'] is not None:
            track.tag()



# finds files with specified extension(s)
def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        files.extend(list(map(str, pathlist)))

    return files



def colorize(text, color):
    if color != '':
        COLOR = {
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "ENDC": "\033[0m",
        }
        return color * COLOR['GREEN'] + (1 - color) * COLOR['RED'] + text + COLOR['ENDC']
    else:
        return text


# parses args
parser = argparse.ArgumentParser()
parser.add_argument('path', help='path to album')

parser.add_argument('-p', '--pattern', nargs='?', help='pattern of track names e.g. <track> - <artist>.flac', default=None)
parser.add_argument('-s', '--spotify', help='search on spotify', action='store_true')
parser.add_argument('-d', '--discogs', help='search on discogs', action='store_true')
args = parser.parse_args()

engines = [spotify, discogs]
if args.spotify:
    engine_num = 0
elif args.discogs:
    engine_num = 1
else:
    # default
    engine_num = 1

path = args.path
pattern = args.pattern

# prepares filename for search, removes junk
query = ' '.join(re.findall('[\w\d]+', ' '.join(path.split('/')[-1:])))
item = 0

engine = engines[engine_num]
album = engine.search_album(query)
match(album, path, pattern)


unsatisfied = True
while unsatisfied:
    resp = input(f'Press enter to continue. Type "n" to get next result. Type "s" to switch engines. Type anything else to manual search.\n')
    if resp == 'n':
        album.next()
        match(album, path, pattern)
    elif resp == "s":
        engine_num = ~engine_num
        engine = engines[engine_num]
        album = engine.search_album(query)
        match(album, path, pattern)
    elif resp != '':
        album = engine.search_album(query)
        match(album, path, pattern)
    else:
        tag_all(album)
        unsatisfied = False







