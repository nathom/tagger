from requests import get
from bs4 import BeautifulSoup
from re import findall, match, sub
import json
from string import ascii_uppercase
from html import unescape

PHONOGRAPHIC_COPYRIGHT = '\u2117'
COPYRIGHT = '\u00a9'

# param: query
# return: dict tags
# searches discogs releases for query
# returns first result by default
def search_album(query, n=0):
    query_formatted = query.replace(' ', '+')
    base_url = 'https://www.discogs.com'
    url = f'https://www.discogs.com/search/?q={query_formatted}&type=release'
    r = get(url)
    soup = BeautifulSoup(r.content, features='lxml')
    links = soup.findAll("a", {"class": "search_result_title"})
    result = str(links[n])
    page = base_url + findall('href="[^"]+"', result)[0][6:-1]
    r = get(page)
    r.encoding = 'utf-8'
    copyright_regex = '<span class="type">[^<]+Copyright[^<]+<\/span>[\s]+–[\s]+<a\ href="[\/\w\d-]+">[\w\d\ ]+<'

    try:
        rights = findall(copyright_regex, unescape(r.text))[0]
        rights2 = findall('>[\w\d\ /(\)]+<', rights)
        right_type = sub('\([cC]\)', COPYRIGHT, rights2[0][1:-1])
        right_type = sub('\([pP]\)', PHONOGRAPHIC_COPYRIGHT, rights2[0][1:-1])
        copyright = right_type + ' ' + rights2[1][1:-1]
    except IndexError:
        copyright = None

    # gets the included json on the top of discogs page source
    start = '<script type="application\/ld\+json" id="release_schema">'
    end = '<\/script>'
    matches = findall(f'{start}[^<]+{end}', r.text)
    plain_text = matches[0][len(start):-len(end)]
    soup = BeautifulSoup(r.text, features='lxml')

    artists = []
    artists_found = soup.find_all('td', {'class': 'tracklist_track_artists'})
    for artist in artists_found:
        a = [s[2:-4] for s in findall('">[^<]+</a>', str(artist))]
        artists.append(a)

    info = json.loads(plain_text)
    for track in info['tracks']:
        track['name'] = unescape(track['name'])

    release = info['releaseOf']
    tracks = info['tracks']
    labels = [label['name'] for label in info['recordLabel']]
    alph = list(ascii_uppercase)
    track_pos = [(alph.index(pos[1:-1][0]) + 1, int(pos[1:-1][1:])) for pos in findall('"[A-Z]\d\d?"', r.text)]

    format = lambda strTime: (int(strTime[2]) * 3600 + int(strTime[4:6].replace('0', '', 1)) * 60 + int(strTime[7:9].replace('0', '', 1)))

    # TODO: make this more efficient/readable
    if len(track_pos) == len(tracks) and len(artists) == len(tracks):
        tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration']), 'pos':track_pos[i], 'artist': artists[i]} for i in range(len(tracks))]

    elif len(track_pos) == len(tracks):
        tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration']), 'pos':track_pos[i]} for i in range(len(tracks))]

    else:
        tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration'])} for i in range(len(tracks))]

    if len(info['genre']) > 3:
        genres = info['genre'][:3]
    else:
        genres = info['genre']

    new_tags = [{
        'TITLE': track['name'],
        'ARTIST': track['artist'] if 'artist' in track else [artist['name'] for artist in release['byArtist']],
        'PERFORMER': track['artist'] if 'artist' in track else [artist['name'] for artist in release['byArtist']],
        'DISCNUMBER': track['pos'][0] if 'pos' in track else None,
        'TRACKNUMBER': track['pos'][1] if 'pos' in track else tracklist.index(track) + 1,
        'GENRE': genres,
        'ALBUMARTIST': [artist['name'] for artist in release['byArtist']],
        'COMPOSER': [artist['name'] for artist in release['byArtist']],
        'TRACKTOTAL': len(tracklist),
        'DISCTOTAL': max([t['pos'][0] for t in tracklist]) if 'pos' in track else None,
        'ALBUM': release['name'],
        'LABEL': labels,
        'COPYRIGHT': copyright,
        'URL': page,
        'DATE': str(release['datePublished']),
        'YEAR': str(release['datePublished'])
    } for track in tracklist]
    return new_tags, info['image']

