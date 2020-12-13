import os
import re
import spotify
import discogs

dir = '/Volumes/nathanbackup/Library/Roedelius/Drauf und Dran'
query = ' '.join(re.findall('[\w\d]+', ' '.join(dir.split('/')[-2:])))
print(query)
album = discogs.search_album(query)
for file in os.listdir(dir):
    for track in album:
        if track.matches(os.path.join(dir, file)):
            track.tag()

for track in album:
    if track['filepath'] is None:
        print(track['title'], track.tracknumber)
