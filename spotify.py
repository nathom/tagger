import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from bases import Track

client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='b69d1047383b485aa4c18906b036fb16', client_secret='01fc99ce735c4ddb8ca509eed50f0e80'))

class search_album(object):
    def __init__(self, query):
        self.curr_item = 0
        self.tracklist = []
        r = client.search(q=f"album:{query}", type='album')
        self.result = r['albums']['items']
        self.get_tags()

    def next(self):
        self.curr_item += 1
        self.get_tags()

    @property
    def album(self) -> dict:
        uri = self.result[self.curr_item]['uri']
        return client.album(uri)

    def get_tags(self) -> None:
        album = self.album.copy()
        disctotal = max([track['disc_number'] for track in album['tracks']['items']])
        self.tracklist = [Track(
            title = track['name'],
            artist = [artist['name'] for artist in track['artists']],
            album = album['name'],
            albumartist = [artist['name'] for artist in album['artists']],
            tracktotal = len(album['tracks']['items']),
            disctotal = disctotal,
            genre = album['genres'],
            copyright = [c['text'] for c in album['copyrights']],
            date = album['release_date'],
            year = album['release_date'][:4],
            label = album['label'],
            pos = (track['disc_number'], track['track_number']),
            cover_url = album['images'][0]['url']
        ) for track in album['tracks']['items']]

    def matches(self, path: str) -> int:
        counter = 0
        for track in self.tracklist:
            for file in os.listdir(path):
                if track.matches(os.path.join(path, file)):
                    counter += 1

        return counter

    def __str__(self):
        return '\n'.join(list(map(str, self.tracklist)))

    def __len__(self):
        return len(self.tracklist)

    def __getitem__(self, key) -> Track:
        return self.tracklist[key]

    def __setitem__(self, key, val):
        self.tracklist[key] = val


class search_track(object):
    def __init__(self, query):
        self.curr_item = 0
        self.track = None
        self.r = client.search(q=query, type='track')
        self.get_tags()

    def next(self):
        self.curr_item += 1
        self.get_tags()

    @property
    def album(self):
        uri = self.result['album']['uri']
        return client.album(uri)

    @property
    def result(self):
        try:
            return self.r['tracks']['items'][self.curr_item]
        except KeyError:
            raise Exception('No results found')

    def get_tags(self):
        result = self.result.copy()
        album = self.album.copy()
        tracklist = album['tracks']['items']

        track_number = 1
        for track in tracklist:
            if track['uri'] == result['uri']:
                track_number = track['track_number']

        disctotal = max([track['disc_number'] for track in album['info']['items']])


        self.track = Track()
        self.track['title'] = result['name']
        self.track['artist'] = [artist['name'] for artist in result['artists']]
        self.track['performer'] = [artist['name'] for artist in result['artists']]
        self.track['genre'] = album['genres']
        self.track['albumartist'] = [artist['name'] for artist in album['artists']]
        self.track['tracknumber'] = track_number
        self.track['tracktotal'] = album['total_tracks']
        self.track['disctotal'] = disctotal
        self.track['album'] = album['name']
        self.track['label'] = album['label']
        self.track['copyright'] = [c['text'] for c in album['copyrights']]
        self.track['date'] = album['release_date']
        self.track['year'] = album['release_date'][:4]
        self.track['cover_url'] = album['images'][0]['url']

    def __str__(self):
        return str(self.track)

    def __getitem__(self, key):
        return self.track[key]

    def __setitem__(self, key, val):
        self.track[key] = val



