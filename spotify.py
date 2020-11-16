from os import system
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

s = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='b69d1047383b485aa4c18906b036fb16', client_secret='01fc99ce735c4ddb8ca509eed50f0e80'))
def search_album(query, n=0):
    r = s.search(q=f"album:{query}", type='album')
    result = r['albums']['items']
    try:
        uri = result[n]['uri']
    except IndexError:
        return

    album_info = s.album(uri)

    tracklist = [{
        'source': 'spotify',
        'type': 'album',
        'name': track['name'],
        'artist': [artist['name'] for artist in track['artists']],
        'pos': (track['disc_number'], track['track_number']),
        'image': album_info['images'][0]['url']
    } for track in album_info['tracks']['items']]

    album = {
        'source': 'spotify',
        'type': 'album',
        'album': album_info['name'],
        'artist': [artist['name'] for artist in album_info['artists']],
        'tracklist': tracklist,
        'numtracks': album_info['total_tracks'],
        'image': album_info['images'][0]['url'],
        'genre': album_info['genres'],
        'year': album_info['release_date'][:4],
        'label': album_info['label'],
        'copyright': [c['text'] for c in album_info['copyrights']]
    }

    return album


def search_track(query, n=0):
    r = s.search(q=query, type='track')

    try:
        result = r['tracks']['items'][n]
    except IndexError:
        return

    album = result['album']

    track = {
        'source': 'spotify',
        'type': 'track',
        'name': result['name'],
        'artist': [artist['name'] for artist in result['artists']],
        'album': album['name'],
        'year': album['release_date'][:4],
        'image': album['images'][0]['url']
    }

    return track

