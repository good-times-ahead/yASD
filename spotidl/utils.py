import os
import subprocess
import platform
from re import search
from urllib.request import urlretrieve

import spotidl.config as config
import spotidl.exceptions as exceptions


default_save_dir = os.getcwd() + "/dl"


def check_env_vars():
    """
    Run a barebones check to ensure that the three needed environment variables
    are not blank.
    """

    client_id, client_secret = os.getenv("SPOTIPY_CLIENT_ID"), os.getenv(
        "SPOTIPY_CLIENT_SECRET"
    )
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    if not client_id:
        raise exceptions.EnvVariablesError("SPOTIPY_CLIENT_ID not configured!")

    elif not client_secret:
        raise exceptions.EnvVariablesError("SPOTIPY_CLIENT_SECRET not configured!")

    elif not redirect_uri:
        raise exceptions.EnvVariablesError("SPOTIPY_REDIRECT_URI not configured!")


# unused, will keep just in case *shrug*
def choice(msg: str) -> bool:
    """
    Offer the user a choice, infinite loop till they make a decision.
    """

    user_choice = ""
    choice_list = ("y", "n")
    while user_choice not in choice_list:
        user_choice = input(msg + ": ")

    return True if user_choice[0].lower() == "y" else False


def make_dir(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)

    except OSError as e:
        print("Error when attempting to make directory: ", e)

    else:
        return True


def check_dir(path: str) -> bool:
    return os.path.isdir(path)


def check_file(path: str) -> bool:
    return os.path.isfile(path)


def directory_maker(path: str):
    """
    Checks for the existence of a directory given the path
    and makes one if it doesn't exist.
    """

    if not check_dir(path):
        if make_dir(path):
            _, dir_name = os.path.split(path)
            print(f"Successfully created '{dir_name}' directory.")


def check_spotify_link(link: str, patterns_list: list) -> bool:
    """
    Handles all checks needed to vet user-entered Spotify links.
    """

    is_match = False

    if not link:
        return is_match

    # patterns_list contains a list of regex patterns for Spotify URLs
    for pattern in patterns_list:
        if search(pattern=pattern, string=link):
            is_match = True

    return is_match


def make_song_title(artists: list, name: str, delim: str):
    """
    Generates a song title by joining the song title and artist names.
    Artist names given in list format are split using the given delimiter.
    """

    return f"{delim.join(artists)} - {name}"


def download_album_art(
    path: str, link: str, title: str, extension: str = "jpeg"
) -> str:
    """
    Downloads album art- in a folder at the given path- to be embedded into songs.
    """

    # make a folder in the given path to store album art
    folder = "/album-art"
    full_path = path + folder
    directory_maker(full_path)

    download_path = full_path + f"/{title}.{extension}"

    if not check_file(download_path):
        urlretrieve(link, download_path)

    return download_path


def check_cli_args(codec: str, bitrate: str, link: str) -> bool:
    """
    Corrects audio-related arguments if they are incorrect and finally calls
    for Spotify link checks.
    """

    # adding checks to ensure argument validity
    if codec not in config.audio_formats:
        # raise argparse.ArgumentTypeError("Invalid codec entered!")
        print("Invalid codec entered! Using default value.")
        codec = "mp3"

    if bitrate not in config.audio_bitrates:
        # raise argparse.ArgumentTypeError("Invalid bitrate entered!")
        print("Invalid bitrate entered! Using default value.")
        bitrate = "320"

    # check whether the provided link is authentic
    is_match = check_spotify_link(link, config.spotify_link_patterns)

    return is_match


def get_link_type(link: str) -> str:
    """
    Analyzes the given link and returns the type of download type required.
    (track for individual song, album for an album URL and playlist if given
    a the Spotify link of a playlist).
    """

    # a spotify link is in the form of: open.spotify.com/<type>/<id>
    # we only need the type part
    type = link.split("/")

    return type[len(type) - 2]


def correct_name(query: str) -> str:
    """
    Checks for illegal characters in file or folder name and corrects them
    if needed.
    """

    for char in config.illegal_chars:
        if char in query:
            query = query.replace(char, "#")

    return query


# since we cannot fetch any playlist data without a playlist id, this will be
# of paramount importance
def get_playlist_id(link: str) -> str:
    """
    Returns a playlist ID given a Spotify playlist URL.
    """

    data = link.split("/")[-1]

    # we can safely return the last part if there's no question mark in it,
    # otherwise we need to split it again to remove the "si" code
    return data.split("?")[0] if "?" in data else data[-1]


# adding a check to see whether ffmpeg is installed since otherwise
# the user gets barraged with a whole lot of tracebacks
# this should simplify that
def check_ffmpeg_installed() -> bool:
    """
    Checks whether FFmpeg is installed or not.
    """

    os_platform = platform.system()

    try:
        if os_platform == "Windows":
            subprocess.check_output(["where", "ffmpeg"])

        subprocess.check_output(["which", "ffmpeg"])

    except Exception:
        return False

    return True
