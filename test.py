import os
import re
import spotify

dir = '/Volumes/nathanbackup/Library/Paul Hiller/Terry Riley_ In C'
query = dir.split('/')[-1]
query = re.sub(r'[^\w^\d^\ ]', '', query)
print(query)
album = spotify.search_album(query)
print(album['album'])
num_matches = album.matches(dir)
print(f'{num_matches}/{len(album)} matched')
for track in album:
    track.tag()
