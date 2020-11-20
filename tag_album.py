from tagger import *
import spotify
import discogs
import argparse

def try_search(query, n=0):
    global path
    global pattern
    global ignore_paren
    tags = engine.search_album(query, n=n)
    if tags:
        try_match(tags, path, pattern=pattern, ignore_paren=ignore_paren)
        return tags
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
print(ignore_paren)
# gets filename from path
filename =  path.split('/')[-1]

# prepares filename for search, removes junk
query = format(filename)
tags = try_search(query)
item = 0
unsatisfied = True
# query until satisfied
while unsatisfied:
    resp = input(f'Press enter to continue. Type \'n\' to get next result. {info} Type anything else to manual search.\n')
    if resp == 'n':
        item += 1
        tags = try_search(query, n=item)
    elif resp == other_abbrev:
        engine = other
        item = 0
        tags = try_search(query)
    elif resp != '':
        item = 0
        tags = try_search(resp, n=item)
    else:
        # get genre tag from discogs if not in spotify API
        if not tags['genre'] and engine is spotify:
            temp_tags = discogs.search_album(tags['album'] + ' ' + ' '.join(tags['artist']))
            if temp_tags:
                tags['genre'] = temp_tags['genre']

        matched_tags, not_matched = match_tags(tags, path)
        unsatisfied = False



input('Press enter to confirm tags.')
set_tags(matched_tags)
print('Finished.')




