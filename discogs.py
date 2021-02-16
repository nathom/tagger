import requests
import re
import json
from string import ascii_uppercase
from html import unescape
from bs4 import BeautifulSoup

from bases import Track

# imports for testing
from pyperclip import copy


# unicode symbols
PHONOGRAPHIC_COPYRIGHT = '\u2117'
COPYRIGHT = '\u00a9'

# param: query
# return: dict tags
# searches discogs releases for query
# returns first result by default

class search_album:
    def __init__(self, query):
        self.base_url = 'https://www.discogs.com'
        self.tracklist = []
        self.curr_item = 0

        query_formatted = query.replace(' ', '+')
        url = f'https://www.discogs.com/search/?q={query_formatted}&type=release'
        results_regex = '<a\ href="([\w\d\/-]+)" class="search_result_title"'
        r = requests.get(url)
        r.encoding = 'utf-8'
        self.results = re.findall(results_regex, r.text)
        self.get_tags()



    @property
    def page(self) -> str:
        if len(self.results) == 0:
            raise Exception('No results found, search again')
        return self.base_url + self.results[self.curr_item]

    def next(self):
        self.curr_item += 1
        self.get_tags()


    def matches(self, path: str) -> int:
        counter = 0
        for track in self.tracklist:
            for file in os.listdir(path):
                if track.matches(os.path.join(path, file)):
                    counter += 1

        return counter

    def get_tags(self):
        r = requests.get(self.page)
        copyright_regex = '<span class="type">([^<]+Copyright[^<]+)<\/span>[^<]+<a href="[^"]+">([^<]+)<\/a>'
        try:
            rights = re.findall(copyright_regex, unescape(r.text))[0]
            right_type = re.sub('\([cC]\)', COPYRIGHT, rights[0])
            right_type = re.sub('\([pP]\)', PHONOGRAPHIC_COPYRIGHT, rights[0])
            copyright = right_type + ' ' + rights[1]#
        except IndexError:
            copyright = None

        # gets the included json on the top of discogs page source
        start = r'<script id="dsdata" type="application\/json">'
        end = r'<\/script>'
        matches = re.findall(f'{start}([\\s\\S]+?){end}', r.text)[0]
        copy(matches)
        info = json.loads(matches)['data']
        release_key = None
        for key in info.keys():
            if 'Release' in key and 'Master' not in key:
                release_key = key

        if release_key is None:
            raise Exception('Release information not found in json')

        for track in info[release_key]['tracks']:
            if track['trackType'] != 'TRACK':
                continue

            # pos = track['position']
            # if pos is none:
                # print(track)
                # continue
            print(track['position'])
            self.__pos_from_alnum(track['position'])

    def __pos_from_alnum(self, position: str) -> tuple:
        '''Get the position as tuple from alphanumeric position
        A1 -> (1, 1)
        D12 -> (4, 12)
        '''
        r = re.findall('(\w)(\d+)', position)
        print(r)



    def __str__(self):
        return '\n'.join([str(s) for s in self.tracklist])

    def __getitem__(self, i):
        return self.tracklist[i]

    def __setitem__(self, i, track):
        self.tracklist[i] = track

    def __len__(self):
        return len(self.tracklist)

