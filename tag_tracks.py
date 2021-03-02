import spotify
import re
from os import listdir
import argparse

# parses arguments
parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to playlist directory")
parser.add_argument(
    "pattern",
    help='put key names in "<>" e.g. "<artist> - <title>.m4a". The "title" key is required.',
)
args = parser.parse_args()

# gets extension of file
ext = lambda path: path.split(".")[-1]
path = args.path
pattern = args.pattern
parent_dir = "/".join(path.split("/")[:-1])
files = listdir(path)

for file in listdir(path):
    # checks if the file is just artwork
    if ext(file) == "jpg":
        continue

    # finds info using pattern and filename
    query = file.replace("." + ext(file), "")
    query = re.sub("[\d-]+", "", query)

    try:
        track = spotify.search_track(query)
    except:
        print(query)
        continue

    track["filepath"] = os.path.join(path, file)
    track.tag()
