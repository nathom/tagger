import tagger
import spotify
import discogs
from pyperclip import paste
import json

dir = paste()
query = dir.split('/')[-1]
tags = discogs.search_album(tagger.format(query) + ' collectors edition', n=0)
print(json.dumps(tags, indent=3))
if tags:
    tagger.try_match(tags, dir)
    #print(m)
