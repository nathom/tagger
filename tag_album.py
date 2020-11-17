from tagger import *
import spotify
import discogs
import argparse

def try_search(query, path, n=0):
    tags = engine.search_album(query, n=n)
    if tags:
        try_match(tags, path)
        return tags
    else:
        print('Matches could not automatically be found.')
        pass

# parses args
parser = argparse.ArgumentParser()
parser.add_argument('path', help='path to album')
parser.add_argument('-s', '--spotify', help='search on spotify', action='store_true')
parser.add_argument('-d', '--discogs', help='search on discogs', action='store_true')
args = parser.parse_args()

if args.spotify:
    engine = spotify
elif args.discogs:
    engine = discogs
else:
    engine = discogs

path = args.path

# gets filename from path
filename =  path.split('/')[-1]

# prepares filename for search, removes junk
query = format(filename)
tags = try_search(query, path)
item = 0
unsatisfied = True
# query until satisfied
while unsatisfied:
    resp = input('Press enter to continue. Type \'n\' to get next result. Type anything else to manual search.\n')
    if resp == 'n':
        item += 1
        tags = try_search(query, path, n=item)
    elif resp != '':
        tags = try_search(resp, path, n=item)
    else:
        # get genre tag from discogs if not in spotify API
        if not tags['genre'] and engine is spotify:
            temp_tags = discogs.search_album(tags['album'] + ' ' + ' '.join(tags['artist']))
            if temp_tags['genre']:
                tags['genre'] = temp_tags['genre']

        matched_tags, not_matched = match_tags(tags, path)
        unsatisfied = False



input('Press enter to confirm tags.')
set_tags(matched_tags)
print('Finished.')




