import requests
from bs4 import BeautifulSoup
from re import findall, sub
import json
from os import listdir, rename, system
from sys import argv

from string import ascii_uppercase
from html import unescape
from progress.bar import IncrementalBar
from curses import tigetnum, setupterm
import music_tag

import discogs


# sets the tags
# param: tag dict with filepath
# return: None
def set_tags(tags, no_disc=False):
    nd = no_disc
    # checks if the 'pos' key exists, if not just use track position
    if not nd:
        try:
            tags['tracklist'][-1]['pos']
        except KeyError:
            nd = True

    # list of genres -> str of genres sep by comma
    genre_str = ''
    for g in tags['genre']:
        genre_str += (g + ', ' * ( len(tags['genre']) > 1 and g != tags['genre'][-1] ))

    # progress bar
    bar = IncrementalBar('Setting tags...', max = len(tags['tracklist']))

    for track in tags['tracklist']:
        bar.next()
        index = tags['tracklist'].index(track)
        try:
            f = music_tag.load_file(track['path'])
        except KeyError:
            continue

        f['album'] = tags['album']
        # check if track has artist listed, else use album artist
        if 'artist' in track:
            artist_str = ''
            for a in track['artist']:
                artist_str += a + ', ' * (len(track['artist']) > 1 and a != track['artist'][-1])

            f['artist'] = artist_str
        else:
            f['artist'] = tags['artist']

        f['totaltracks'] = tags['numtracks']
        f['tracktitle'] = track['name']
        f['year'] = tags['year']

        if nd:
            f['tracknumber'] = index + 1
        else:
            f['discnumber'] = track['pos'][0]
            f['tracknumber'] = track['pos'][1]

        f['genre'] = genre_str

        # sets the artwork
        album = tags['album'].replace('/', '|')
        title = track['name']
        art = requests.get(tags['image'])
        img_path = f'/Volumes/nathanbackup/Music/Artwork/{album}.jpg'
        open(img_path, 'wb').write(art.content)

        with open(img_path, 'rb') as img_in:
            f['artwork'] = img_in.read()

        f.save()

    bar.finish()


# matches tags with filepaths
# param tags: dict tags
# param dir_path: path of directory to search
# return tuple: (dict: tags with 'path' key, list: files not matched)
# TODO: improve matching algorithm

def match_tags(tags, dir_path):
    tracklist = [{'formatted': format2(track['name']), 'orig':tags['tracklist'].index(track)} for track in tags['tracklist']]
    pathlist = listdir(dir_path)
    pathlist = [{'formatted': format2(path.split('/')[-1]), 'orig':f'{dir_path}/{path}'} for path in pathlist]
    pprint = lambda s: print(json.dumps(s, indent=3))

    counter = 0
    for track in tracklist:
        for path in pathlist:
            if matches(track['formatted'], path['formatted']):
                counter += 1
                tags['tracklist'][track['orig']]['path'] = path['orig']

    # right now there are repeats so that counter > len(pathlist)
    # TODO: fix it by making the matching more strict
    return tags, len(pathlist) - counter






# Utilities

# makes text red or green
# param color: 0 for red, 1 for green
# return colored text
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

# checks if word is in name
# every word in the discogs track name must be in each file name
# case insensitive
# ignores single quotes
def matches(word, name):
    if word == name:
        return True

    r = findall(f'(?i){word}', name)
    if len(r) == 0:
        return matches_final(word, name)
    else:
        return True

def matches_final(word, name, forgive=2):
    buffer = []
    errors = 0
    name = list(format(name))
    word = list(format(word))

    not_matched = True

    curr = 0
    if len(word) == 0 or len(name) == 0:
        return False

    while name[0].lower() != word[0].lower():
        if len(name) > 1:
            name.pop(0)
        else:
            return False


    # case 1: substitution
    if len(name) == len(word):
        for i in range(len(name)):
            if name[i] != word[i]:
                errors += 1
            if errors > forgive:
                return False

    # case 2: frameshift (insertion/deletion)
    else:
        large = name if len(name) > len(word) else word
        small = name if len(name) < len(word) else word
        if len(large)//len(small) >= 2:
            return False

        curr = 0
        while True:
            if large[curr] != small[curr]:
                errors += 1
                large.pop(curr)
                curr = 0
            curr += 1
            if curr == len(small) - 1:
                break
            if len(large) == 0 or errors > forgive:
                return False

    return True

def try_match(tags, path):
    setupterm()
    cols = tigetnum('cols')
    getFilename = lambda path: path.split('/')[-1]
    matched_tags, not_matched = match_tags(tags, path)
    not_found = 0
    album = matched_tags['album']
    artist = ''
    for g in matched_tags['artist']:
        artist += (g + ', ' * ( len(matched_tags['artist']) > 1 and g != matched_tags['artist'][-1] ))

    print(f'{artist} - {album}', end='\n\n')
    for track in matched_tags['tracklist']:
        try:
            name = colorize(track['name'], 1) + ' \u2192 '
            path = getFilename(track['path'])
            print(name, end='')
            print(path.rjust(cols*3//5))
        except KeyError:
            name = colorize(track['name'], 1) + ' \u2192 '
            print(name, end='')
            print(colorize('Not found', 0))
            not_found += 1
            pass

    print(f'{not_matched} file(s) not matched.')





def set_track_tags(track):
    f = music_tag.load_file(track['path'])
    parent_dir = '/'.join(track['path'].split('/')[:-1])

    f['album'] = track['album']
    f['artist'] = track['artist']
    f['tracktitle'] = track['name']
    f['year'] = track['year']

    # sets the artwork
    album = track['album']
    art = requests.get(track['image'])
    img_path = f'{parent_dir}/cover.jpg'
    open(img_path, 'wb').write(art.content)

    with open(img_path, 'rb') as img_in:
        f['artwork'] = img_in.read()

    f.save()

'''
given pattern like '$artist - $track.m4a' and a filename 'the beatles - back in the ussr.m4a'
returns dict = {
    'artist': 'the beatles',
    'track': 'back in the ussr'
    ...
}
'''
def parse_filenames(pattern, name):
    is_var = False
    possible_vars = ['$artist', '$track', '$album', '$year', '$id']
    buffer = []
    vars = []
    for char in pattern:
        if char == '$':
            is_var = True
        if is_var:
            buffer.append(char)
        joined = ''.join(buffer)
        if joined in possible_vars:
            vars.append(joined)
            is_var = False
            buffer = []

    # gets everything that isn't a var in the pattern
    remaining = get_surrounding(pattern, vars)
    # gets everything that isn't in the surroundings
    # end up with a list of the values
    final_values = get_surrounding(name, remaining)
    info = {}
    for i in range(len(vars)):
        info[vars[i][1:]] = final_values[i]

    return info

# returns list of surroundings of a string given vars
'''
example:
vars = ['foo', 'bar']
s = 'this isfooand    bar and some other things'
returns ['this is', 'and   ', ' and some other things']
'''
def get_surrounding(s, vars):
    surr = s.split(vars[0])
    for item in surr:
        if vars[1] in item:
            surr.extend(item.split(vars[1]))
            surr.remove(item)

    if '' in surr: surr.remove('')
    return surr

# formats the file name for searching
def format(track):
    track = track.replace('.m4a', '')
    track = track.replace('.flac', '')
    track = track.replace(' - ', ' ')
    track = track.replace("'", '')
    track = track.replace('"', '')
    track = track.replace('_', '')
    # removes anything inside ()
    track = sub('\([^\(|^\)]+\)', '', track)
    # removes anything inside []
    track = sub('\[[^\[|^\]]+\]', '', track)
    # removes feat. ...
    track = sub('[fF]eat[\s\S]+', '', track)
    track = track.strip()
    # removes anything thats not a letter or number
    # f = findall('[\w|\d|\ ]+', track)
    # track = ' '.join(f)

    return track

def format2(s):
    formatted = ' '.join(findall('[a-zA-Z]+', s.replace('.m4a', ''))).strip()
    formatted = formatted.replace('  ', ' ')
    return formatted


