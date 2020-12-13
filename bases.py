import json
import re
import requests
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover


_mp4_keys = {
    'title': r'©nam',
    'artist': r'©ART',
    'album': r'©alb',
    'albumartist': r'aART',
    'composer': r'©day',
    'year': r'©day',
    'comment': r'©cmt',
    'description': 'desc',
    'purchase_date': 'purd',
    'grouping': r'©grp',
    'genre': r'©gen',
    'lyrics': r'©lyr',
    'encoder': r'©too',
    'copyright': 'cprt',
    'compilation': 'cpil',
    'cover': 'covr',
    'tracknumber': 'trkn',
    'discnumber': 'disk'
}



class Track(object):
    def __init__(self, **kwargs):
        self.filepath = None

        self.title = None
        self.artist = None
        self.album = None
        self.pos = None
        self.date = None
        self.year = None
        self.genre = None
        self.copyright = None
        self.label = None
        self.albumartist = None
        self.url = None
        self.length = None
        self.cover_url = None
        self.tracktotal = None
        self.disctotal = None

        for k, v in kwargs.items():
            self.__dict__[k] = v

    def tag(self) -> None:
        if self.filepath is None:
            raise AttributeError(f'Filepath of "{self.title}" not set')

        if self.ext == 'flac':
            audio = FLAC(self.filepath)
            for k, v in self.__dict__.items():
                # TODO: fix composer glitch where it displays as list
                if k in ['ARTIST', 'COMPOSER', 'GENRE', 'ALBUMARTIST'] and type(v) is list:
                    audio[k.upper()] = self._format_list(v)
                elif k not in ['filepath', 'cover_url', 'pos', 'length']:
                    audio[k] = str(v)

            audio.save()
        elif self.ext == 'm4a':
            audio = MP4(self.filepath)
            for k, v in self.__dict__.items():
                if k not in ['filepath', 'cover_url', 'pos', 'length', 'date', 'label', 'url', 'tracktotal', 'disctotal', 'artist'] and v is not None:
                    audio[_mp4_keys[k]] = v
                elif k in ['artist']:
                    audio[_mp4_keys[k]] = _format_list(v)

            audio[_mp4_keys['tracknumber']] = [(self.tracknumber, self.tracktotal)]
            audio[_mp4_keys['discnumber']] = [(self.discnumber, self.disctotal)]
            audio['covr'] = self.images
            audio.save()


    def matches(self, path: str, change_path=True, pattern=None) -> bool:
        '''Checks if the track title matches a filepath.
        Use an absolute path or set change_path to False.
        See _parse_pattern docstring for how to use a pattern.'''

        if pattern is not None:
            p = _parse_pattern(pattern, path.split('/')[-1])
            if 'title' not in p:
                raise AttributeError('Must have a <title> key in pattern.')
            search_path = p['title']
        else:
            search_path = path

        m = _matches(_format_title(self.title), _format_title(search_path))
        if change_path and m:
            self.filepath = path

        return m



    @property
    def tracknumber(self) -> int:
        return self.pos[1]

    @tracknumber.setter
    def tracknumber(self, val) -> int:
        self.pos[1] = val

    @property
    def discnumber(self) -> int:
        return self.pos[0]

    @discnumber.setter
    def discnumber(self, val) -> int:
        self.pos[0] = val


    @property
    def ext(self) -> str:
        if self.filepath is not None:
            return self.filepath.split('.')[-1]
        else:
            raise AttributeError(f'Filepath of "{self.title}" not set')

    @property
    def images(self) -> list:
        if self.cover_url.endswith('jpg'):
            fmt = MP4Cover.FORMAT_JPEG
        else:
            fmt = MP4Cover.FORMAT_PNG


        r = requests.get(self.cover_url)
        return [MP4Cover(r.content, imageformat=fmt)]


    def __str__(self):
        d = {}
        for k, v in self.__dict__.items():
            if v is not None:
                d[k] = v

        return json.dumps(d, indent=3)

    def __repr__(self):
        return json.dumps(self.__dict__, indent=2)


    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, val):
        self.__dict__[key] = val




def _matches(track: str, path: str, forgive=2) -> bool:
    '''Checks if the track matches with the filepath.
    There are three cases with different behaviors:
        * they are exactly the same (after formatting)
        * they have the same length but not the same
        * neither of the above

    '''

    if track == path:
        return True

    if len(track) == len(path):
        return _direct_match(track, path, forgive=forgive)
    else:
        return _frameshift_match(track, path, forgive=forgive)


def _direct_match(first: str, second: str, forgive=2) -> bool:
    '''This checks if each character at the same index matches'''
    errors = 0
    first, second = list(first.lower()), list(second.lower())
    for i in range(len(first)):
        if first[i] != second[i]:
            errors += 1
        if errors > forgive:
            return False
    return True

def _frameshift_match(first: str, second: str, forgive=2) -> bool:
    '''If the length isnt the same, it will remove characters until they match or exceed forgiveness '''

    first, second = list(first.lower()), list(second.lower())
    errors = 0
    not_matched = True
    i = 0
    while True:
        if i > len(second) - 1 or i > len(first) - 1:
            break

        if first[i] != second[i]:
            errors += 1
            longer = first if len(first) > len(second) else second
            longer.pop(i)
            i -= 1
        if errors > forgive:
            return False

        if first == second:
            return True

        i += 1
    longer = first if len(first) > len(second) else second
    shorter = first if len(first) < len(second) else second
    # if the longer one has excess that can be forgiven
    if longer[:len(shorter)] == shorter and errors + (len(longer) - len(shorter)) <= forgive:
        return True

def _format_title(s: str, paren=False) -> str:
    # find words, only letters, without ext
    # removes feat. ...
    if '/' in s:
        s = s.split('/')[-1]

    s = re.sub('[fF]eat[\s\S]+', '', s)
    if paren:
        # removes anything inside ()
        s = re.sub('\([^\(|^\)]+\)', '', s)
        # removes anything inside []
        s = re.sub('\[[^\[|^\]]+\]', '', s)

    s = re.sub('(\.flac|\.m4a|\.wav)', '', s)
    s = re.sub('[\'"]', '', s)
    formatted = ' '.join(re.findall('[a-zA-Z]+', s)).strip()
    formatted = formatted.replace('  ', ' ')
    return formatted

def _parse_pattern(pattern: str, s: str) -> dict:
    '''Parses patterns that specify information in the filename.
    This is useful for removing artifacts that may be missed by the formatter.

    >>> path = "02 Angela (2020 Remaster).m4a"
    >>> pattern = _parse_pattern('<tracknumber> <title> (<ignore>)', path)
    >>> pattern
    {'tracknumber': '02', 'title': 'Angela', 'ignore': '2020 Remaster'}

    You can replace "ignore" with anything except reserved attributes, or leave it empty:
    >>> pattern = _parse_pattern('<tracknumber> <title> (<>)', path)
    >>> pattern
    {'tracknumber': '02', 'title': 'Angela', '': '2020 Remaster'}

    Only the "title" key is used for searching in this class.
    '''

    curr_key = ''
    curr_val = ''
    keys = []
    vals = []

    delim = ''
    i = j = 0
    while i < len(pattern):
        if pattern[i] == '<':
            # adds var name to keys
            i += 1
            while pattern[i] != '>':
                curr_key += pattern[i]
                i += 1
            i += 1
            keys.append(curr_key)
            curr_key = ''

            # gets chars in between variables or end of string
            while i < len(pattern) and pattern[i] != '<':
                delim += pattern[i]
                i += 1

            # checks whether the next set of chars match delim
            while s[j:j + len(delim)] != delim:
                curr_val += s[j]
                j += 1

            # shifts j so that delim is not included in the next round
            j += len(delim)

            vals.append(curr_val)
            curr_val = ''
            delim = ''


        else:
            i += 1
            j += 1


    return dict(zip(keys, vals))



def _format_list(l: list) -> str:
    '''Puts commas (,) in between items in the list'''

    s = ''
    for g in l:
        s += (g + ', ' * ( len(l) > 1 and g != l[-1] ))
    return s





