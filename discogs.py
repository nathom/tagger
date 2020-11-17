from requests import get
from bs4 import BeautifulSoup
from re import findall
import json
from string import ascii_uppercase
from html import unescape

# param: query
# return: dict tags
# searches discogs releases for query
# returns first result by default
def search_album(query, n=0):
    query_formatted = query.replace(' ', '+')
    base_url = 'https://www.discogs.com'
    url = f'https://www.discogs.com/search/?q={query_formatted}&type=release'
    r = get(url)
    try:
        soup = BeautifulSoup(r.content, features='lxml')
        links = soup.findAll("a", {"class": "search_result_title"})
        result = str(links[n])
        page = base_url + findall('href="[^"]+"', result)[0][6:-1]
        r = get(page)
        r.encoding = 'utf-8'

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
    except:
        return None

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

    tags = {
        'album' : release['name'], # String
        'artist': [artist['name'] for artist in release['byArtist']], # list
        'numtracks': release['numTracks'], # int
        'tracklist' : tracklist, #list of dicts -> {name:String, duration:int secs, (optional)pos: (int disc, track)}
        'image' : info['image'], #url
        'genre' : genres, #list of genres
        'year' : str(release['datePublished']), #int
        'label': labels
    }
    return tags

