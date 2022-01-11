from dotenv.main import load_dotenv
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from dataclasses import dataclass

import exceptions as e 
import utils as u 

# loading .env variables
load_dotenv()
# todo: trigger an error if the required env variables not found!

# initializing the spotify api connection
# the OAuth object automatically reads valid env. variables so we don't need to
# manually assign them using `os.environ.get(<env_var name>)` 
sp = Spotify(auth_manager=SpotifyOAuth())


# defining structure for the song data we are going to be parsing
@dataclass
class SpotifySong:
    name: str
    artists: dict
    album_name: str
    disc_number: int
    track_number: int
    cover_url: str

    def __str__(self):
        artists = []
        for artist in self.artists:
            artists.append(artist["name"])

        return u.make_song_title(artists, self.name, ", ")


def get_song_data(link: str) -> SpotifySong:
    """
    Gets relevant song details for the given Spotify song link.
    These are then passed onto other functions for further processing.
    """

    try:
        query = sp.track(link)

    except SpotifyException as e:
        # wrapping the Spotify Exception
        # still unsure whether this is the correct approach
        raise e.NoDataReceivedError(e)

    else:
        # there can be multiple results,
        # iterating over the list and extracting data
        artists = []
        for artist in query["artists"]:
            artists.append(artist["name"])

        song = new_song(query, type="song")

        return song


# this will serve as the common point for all entry types
# (individual song link, album link, etc.) 
def new_song(query: dict, type: str, **album_details) -> SpotifySong:
    """
    Makes a new SpotifySong given a raw "track" type item received from Spotify API.
    The track queried using different methods returns slightly modified data.
    """

    artists = []
    for artist in query["artists"]:
        artists.append(artist["name"])

    name = u.correct_name(query["name"])

    match type:
        # "song" refers to the case where the user enters a song link; we need
        # to fetch data for just a single song 
        case "song":
            song = SpotifySong(
            name=name,
            artists=artists,
            album_name=query["album"]["name"],
            disc_number=query["disc_number"],
            track_number=query["track_number"],
            # the 1st link contains a link to the album art
            # of size 640 x 640 pixels
            cover_url=query["album"]["images"][0]["url"],
        )

        case "album":
            song = SpotifySong(
            name=name, 
            artists=artists,
            album_name=album_details["album_name"],
            disc_number=query["disc_number"],
            track_number=query["track_number"],
            cover_url=album_details["album_cover_url"],
        )

    
    return song 


def get_album_data(link: str) -> tuple:
    """
    Gets album data for the given Spotify album link.
    It is then passed onto other functions for further processing.
    """

    # since our main data(all the relevant metadata, song URL) is associated
    # with the spotify song(referred to as "Track" in the spotify api), we
    # will need to make a list of all the songs in the album and then pass on
    # that list onto other functions.
    try:
        query = sp.album(link)

    except SpotifyException as ex:
        e.NoDataReceivedError(ex)

    album: list[SpotifySong] = []
    album_name = u.correct_name(query["name"])

    for track in query["tracks"]["items"]:
        # since this time we are directly receiving data that we otherwise
        # extracted from get_song_data using a link entered by the user, we
        # will need to generate a SpotifySong object another way

        song = new_song(track, type="album", 
        album_name=album_name, 
        album_cover_url=query["images"][0]["url"])

        album.append(song)

    # returning album name since we'll need it when making the album folder to
    # use as the save directory
    return (album_name, album)



def get_playlist_data(link: str) -> tuple:
    """
    Gets playlist data for the given Spotify playlist link.
    It is then passed onto other functions for further processing.
    """

    # we need playlist id to fetch its information
    playlist_id = u.get_playlist_id(link)

    try:
        query = sp.playlist_tracks(playlist_id)
        playlist_name = sp.playlist(playlist_id)["name"]

    except SpotifyException as ex:
        raise e.NoDataReceivedError(ex)

    # can fetch a 100 tracks at a time
    # the "next" dictionary key gets the next batch, if the no. of results
    # exceeds 100
    tracks = query["items"]

    while query["next"]:
        query = sp.next(query)
        tracks.extend(query["items"])

    # now, to extract data from each entry in the list and get a SpotifySong object
    playlist_songs: list[SpotifySong] = []

    for track in tracks:
        song = new_song(track["track"], type="song")
    
        playlist_songs.append(song)

    return playlist_name, playlist_songs

if __name__ == "__main__":

    song = get_song_data(
        "https://open.spotify.com/track/0Ey8buiWgtBQjb7ypaACKN?si=22882b3a21ae4c71"
    )
    print(song)

    album = get_album_data(
        "https://open.spotify.com/album/0bWYlK9rRmIB68icHx9PNR?si=0PRvNMbBSticZvfdCeGdjw"
    )
    print(album[0])