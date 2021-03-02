import requests
import re
import json
from string import ascii_uppercase
from html import unescape
from bs4 import BeautifulSoup

from bases import Track

# imports for testing
from pyperclip import copy


# unicode symbols
PHONOGRAPHIC_COPYRIGHT = "\u2117"
COPYRIGHT = "\u00a9"

# param: query
# return: dict tags
# searches discogs releases for query
# returns first result by default


class search_album:
    def __init__(self, query):
        self.base_url = "https://www.discogs.com"
        self.tracklist = []
        self.curr_item = 0

        query_formatted = query.replace(" ", "+")
        self.url = f"https://www.discogs.com/search/?q={query_formatted}&type=release"
        results_regex = '<a\ href="([\w\d\/-]+)" class="search_result_title"'
        r = requests.get(self.url)
        r.encoding = "utf-8"
        self.results = re.findall(results_regex, r.text)
        self.get_tags()

    @property
    def page(self) -> str:
        if len(self.results) == 0:
            raise Exception("No results found, search again")
        return self.base_url + self.results[self.curr_item]

    def next(self):
        self.curr_item += 1
        self.get_tags()

    def matches(self, path: str) -> int:
        counter = 0
        for track in self.tracklist:
            for file in os.listdir(path):
                if track.matches(os.path.join(path, file)):
                    counter += 1

        return counter

    def get_tags(self):
        r = requests.get(self.page)
        copyright_regex = '<span class="type">([^<]+Copyright[^<]+)<\/span>[^<]+<a href="[^"]+">([^<]+)<\/a>'
        try:
            rights = re.findall(copyright_regex, unescape(r.text))[0]
            right_type = re.sub("\([cC]\)", COPYRIGHT, rights[0])
            right_type = re.sub("\([pP]\)", PHONOGRAPHIC_COPYRIGHT, rights[0])
            copyright = right_type + " " + rights[1]  #
        except IndexError:
            copyright = None

        # gets the included json on the top of discogs page source
        start = r'<script id="dsdata" type="application\/json">'
        end = r"<\/script>"
        matches = re.findall(f"{start}([\\s\\S]+?){end}", r.text)[0]
        copy(matches)
        info = json.loads(matches)["data"]
        release_key = None
        image_key = None
        for key in info.keys():
            if "Release" in key and "Master" not in key:
                release_key = key
            elif "Image" in key and "}" not in key:
                image_key = key

        if release_key is None:
            raise Exception("Release information not found in json")
        if image_key is None:
            raise Exception("Image info not found in json.")

        self.__parse_track_info(info[release_key], info[image_key])

    # TODO: make it so that discs have two sides instead of one
    def __parse_track_info(self, album: dict, img: dict) -> None:
        # get copyright, phonographic cr, and label
        copyrights = []
        album_label = None
        for label in album["labels"]:
            if label["labelRole"] == "PHONOGRAPHIC_COPYRIGHT":
                copyrights.append(f'{PHONOGRAPHIC_COPYRIGHT} {label["label"]["name"]}')
            elif label["labelRole"] == "COPYRIGHT":
                copyrights.append(f'{COPYRIGHT} {label["label"]["name"]}')
            elif label["labelRole"] == "LABEL":
                album_label = label["label"]["name"]

        # values that all tracks share
        album_artists = [artist["artist"]["name"] for artist in album["primaryArtists"]]
        global_info = {
            "album": album["title"],
            "artist": album_artists,
            "albumartist": album_artists,
            "genre": ", ".join(album["genres"][:3]),
            "year": album["released"][:4],
            "label": album_label,
            "copyright": " ".join(copyrights),
            "date": album["released"],
            # deal with wierd formatting in json
            "cover_url": re.findall(r'https[^"]+', img["fullsize"]["__ref"])[0],
            "url": self.url,
        }

        pos_list = []
        # set values
        for track in album["tracks"]:
            # this means it is a heading or something else
            if track["trackType"] != "TRACK":
                continue

            t = Track(**global_info)
            t.title = track["title"]
            t.length = track["durationInSeconds"]

            t.pos = self.__pos_from_alnum(track["position"])
            pos_list.append(t.pos)

            self.tracklist.append(t)

        # post-processing
        tracktotal = len(pos_list)
        disctotal = max((p[0] for p in pos_list))
        for track in self.tracklist:
            track.tracktotal = tracktotal
            track.disctotal = disctotal

    def __pos_from_alnum(self, position: str) -> tuple:
        """Get the position as tuple from alphanumeric position
        A1 -> (1, 1)
        D12 -> (4, 12)
        """
        r = re.findall("(\w)(\d+)", position)[0]
        # convert letter to number (starting at 1)
        return (ascii_uppercase.index(r[0]) + 1, int(r[1]))

    def __str__(self):
        return "\n".join([str(s) for s in self.tracklist])

    def __getitem__(self, i):
        return self.tracklist[i]

    def __setitem__(self, i, track):
        self.tracklist[i] = track

    def __len__(self):
        return len(self.tracklist)
