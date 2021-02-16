import requests
import re
import json
from string import ascii_uppercase
from html import unescape
from bs4 import BeautifulSoup

from bases import Track
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
        print(url)
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
        start = '<script type="application\/ld\+json" id="release_schema">'
        end = '<\/script>'
        matches = re.findall(f'{start}[^<]+{end}', r.text)
        plain_text = matches[0][len(start):-len(end)]
        soup = BeautifulSoup(r.text, features="html.parser")

        artists = []
        artists_found = soup.find_all('td', {'class': 'tracklist_track_artists'})
        for artist in artists_found:
            a = [s[2:-4] for s in re.findall('">[^<]+</a>', str(artist))]
            artists.append(a)

        print(plain_text)
        info = json.loads(plain_text)
        for track in info['tracks']:
            track['name'] = unescape(track['name'])

        release = info['releaseOf']
        tracks = info['tracks']
        labels = [label['name'] for label in info['recordLabel']]
        alph = list(ascii_uppercase)
        track_pos = [(alph.index(pos[1:-1][0]) + 1, int(pos[1:-1][1:])) for pos in re.findall('"[A-Z]\d\d?"', r.text)]
        if track_pos == []:
            track_pos = [(1, i) for i in range(1, len(tracks)+1)]


        format = lambda str_time: (int(str_time[2]) * 3600 + int(str_time[4:6].replace('0', '', 1)) * 60 + int(str_time[7:9].replace('0', '', 1)))

        if len(track_pos) == len(tracks) == len(artists):
            self.tracklist = [Track(
                title = unescape(tracks[i]['name']),
                length = format(tracks[i]['duration']),
                pos = track_pos[i],
                artist = artists[i])
            for i in range(len(tracks))]

        elif len(track_pos) == len(tracks):
            self.tracklist = [Track(
                title = unescape(tracks[i]['name']),
                length = format(tracks[i]['duration']),
                pos = track_pos[i])
            for i in range(len(tracks))]

        else:
            self.tracklist = [Track(
                title = unescape(tracks[i]['name']),
                length = format(tracks[i]['duration']))
            for i in range(len(tracks))]

        genre = info['genre'][0]

        for track in self.tracklist:
            track['genre'] = genre
            track['cover_url'] = info['image']
            track['year'] = str(info['releaseOf']['datePublished'])
            track['date'] = str(info['releaseOf']['datePublished'])
            track['tracktotal'] = len(self.tracklist)
            track['disctotal'] = max([t['pos'][0] for t in self.tracklist])

            track['url'] = self.page
            track['album'] = info['releaseOf']['name']
            track['copyright'] = copyright
            if track['artist'] is None:
                track['artist'] = artists


    def __str__(self):
        return '\n'.join([str(s) for s in self.tracklist])

    def __getitem__(self, i):
        return self.tracklist[i]

    def __setitem__(self, i, track):
        self.tracklist[i] = track

    def __len__(self):
        return len(self.tracklist)

