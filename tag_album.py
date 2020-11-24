from tagger import *
import spotify
import discogs
import argparse

def try_search(query, n=0):
    global path
    global pattern
    global ignore_paren
    tags, cover = engine.search_album(query, n=n)
    if tags:
        try_match(tags, path, pattern=pattern, ignore_paren=ignore_paren)
        return tags, cover
    else:
        print('Matches could not automatically be found.')
        pass

# parses args
parser = argparse.ArgumentParser()
parser.add_argument('path', help='path to album')

parser.add_argument('-p', '--pattern', nargs='?', help='pattern of track names e.g. $track - $artist.flac', default=None)
parser.add_argument('-ip', '--ignore-parentheses', help='ignore things in brackets or parentheses when matching filenames with tracks', action='store_true')
parser.add_argument('-s', '--spotify', help='search on spotify', action='store_true')
parser.add_argument('-d', '--discogs', help='search on discogs', action='store_true')
args = parser.parse_args()

if args.spotify:
    engine = spotify
    other = discogs
    other_abbrev = 'd'
    info = "Type 'd' to switch search engine to discogs."
elif args.discogs:
    engine = discogs
    other = spotify
    other_abbrev = 's'
    info = "Type 's' to switch search engine to spotify."
else:
    # default
    engine = discogs
    other = spotify
    other_abbrev = 's'
    info = "Type 's' to switch search engine to spotify."


path = args.path
pattern = args.pattern
ignore_paren = args.ignore_parentheses
# gets filename from path
filename =  path.split('/')[-1]

# prepares filename for search, removes junk
query = format(filename)
tags, cover = try_search(query)
item = 0
unsatisfied = True
# query until satisfied
while unsatisfied:
    resp = input(f'Press enter to continue. Type \'n\' to get next result. {info} Type anything else to manual search.\n')
    if resp == 'n':
        item += 1
        tags, cover = try_search(query, n=item)
    elif resp == other_abbrev:
        engine = other
        item = 0
        tags, cover = try_search(query)
    elif resp != '':
        item = 0
        tags, cover = try_search(resp, n=item)
    else:
        # get genre tag from discogs if not in spotify API
        if not tags[0]['GENRE'] and engine is spotify:
            try:
                temp_tags, temp_cover = discogs.search_album(tags[0]['ARTIST'] + ' ' + ' '.join(tags[0]['ARTIST']))
                if temp_tags:
                    tags[0]['GENRE'] = temp_tags[0]['GENRE']
            except:
                pass

        matched_tags, not_matched = match_tags(tags, path)
        unsatisfied = False



input('Press enter to confirm tags.')
set_tags(matched_tags, cover)
print('Finished.')




