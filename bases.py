import json
from mutagen.flac import FLAC, Picture


class Track(object):
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

    def set(self) -> None:
        if self.filepath is None:
            raise AttributeError(f'Filepath of {self.name} not set')

        if self.ext == 'flac':
            audio = FLAC(self.filepath)
            for k, v in self.__dict__.items():
                # TODO: fix composer glitch where it displays as list
                if k in ['ARTIST', 'COMPOSER', 'GENRE', 'ALBUMARTIST'] and type(v) is list:
                    audio[k.upper()] = self._format_list(v)
                else:
                    audio[k] = str(v)

            audio.save()
        elif self.ext == 'm4a':
            audio = MP4(self.filepath)
            for k, v in self.__dict__.items():
                audio[self._mp4_keys[k]] = v

            audio['covr'] = self.images



    def _format_list(self, l: list) -> str:
        '''Puts commas (,) in between items in the list'''

        s = ''
        for g in l:
            s += (g + ', ' * ( len(l) > 1 and g != l[-1] ))
        print(type(s))
        return s


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


    @property
    def tracknumber(self):
        return self.pos[1]

    @tracknumber.setter
    def tracknumber(self, val):
        self.pos[1] = val

    @property
    def discnumber(self):
        return self.pos[0]

    @discnumber.setter
    def discnumber(self, val):
        self.pos[0] = val

    @property
    def ext(self):
        if self.filepath is not None:
            return self.filepath.split('.')[-1]
        else:
            raise AttributeError(f'Filepath of {self.name} not set')

    @property
    def images(self):
        if self.cover_url.endswith('jpg'):
            fmt = MP4Cover.FORMAT_JPEG
        else:
            fmt = MP4Cover.FORMAT_PNG


        r = get(self.cover_url)
        return [MP4Cover(r.content, imageformat=fmt)]


