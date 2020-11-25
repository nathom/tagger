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
        return None, None

    album_info = s.album(uri)

    tracklist = [{
        'source': 'spotify',
        'type': 'album',
        'name': track['name'],
        'artist': [artist['name'] for artist in track['artists']],
        'pos': (track['disc_number'], track['track_number']),
        'image': album_info['images'][0]['url']
    } for track in album_info['tracks']['items']]


    new_tags = [{
        'TITLE': track['name'],
        'ARTIST': track['artist'],
        'PERFORMER': track['artist'],
        'DISCNUMBER': track['pos'][0],
        'TRACKNUMBER': track['pos'][1],
        'GENRE': album_info['genres'],
        'ALBUMARTIST': [artist['name'] for artist in album_info['artists']],
        'TRACKTOTAL': len(tracklist),
        'DISCTOTAL': max([t['pos'][0] for t in tracklist]),
        'ALBUM': album_info['name'],
        'LABEL': album_info['label'],
        'COPYRIGHT': [c['text'] for c in album_info['copyrights']],
        'DATE': album_info['release_date'],
        'YEAR': album_info['release_date'][:4]
    } for track in tracklist]


    return new_tags, album_info['images'][0]['url']

def search_track(query, n=0):
    r = s.search(q=query, type='track')

    try:
        result = r['tracks']['items'][n]
    except IndexError:
        return

    album_uri = result['album']['uri']
    album = s.album(album_uri)
    tracklist = album['tracks']['items']

    track_number = 1
    total_tracks = 0
    for track in tracklist:
        total_tracks += 1
        if track['uri'] == result['uri']:
            track_number = track['track_number']

    new_tags = [{
        'TITLE': result['name'],
        'ARTIST': [artist['name'] for artist in result['artists']],
        'PERFORMER': [artist['name'] for artist in result['artists']],
        'TRACKNUMBER': track_number,
        'GENRE': album['genres'],
        'ALBUMARTIST': [artist['name'] for artist in album['artists']],
        'TRACKTOTAL': album['total_tracks'],
        'ALBUM': album['name'],
        'LABEL': album['label'],
        'COPYRIGHT': [c['text'] for c in album['copyrights']],
        'DATE': album['release_date'],
        'YEAR': album['release_date'][:4]
    } for track in tracklist]

    return new_tags, album['images'][0]['url']

