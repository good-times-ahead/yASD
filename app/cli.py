import argparse
import os

import utils as u
import spotify as s
import youtube as y
import config as c
import exceptions as e
import metadata as m


def cli_args():
    """
    Contains and parses all command line arguments for the application.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="Spotify song link to download")

    # important argument(s)
    parser.add_argument(
        "-d",
        "--dir",
        default=u.default_save_dir,
        help="Save directory(is created if doesn't exist)",
    )

    parser.add_argument(
        "-t",
        "--type",
        default="track",
        help=f"Download type of the given link. Can be {c.spotify_link_types}",
    )

    # audio-related arguments
    # quiet is stored to be True, means we don't have to enter anything
    # after calling "-q/--quiet", it defaults to True if called else False
    parser.add_argument(
        "-q",
        "--quiet",
        # default=False,
        action="store_true",
        help="Makes the downloader non-verbose/quiet",
    )

    parser.add_argument(
        "-c",
        "--codec",
        default="mp3",
        help=f"Audio format to download file as. List of available formats: {c.audio_formats}",
    )

    parser.add_argument(
        "-b",
        "--bitrate",
        default="320",
        help=f"Audio quality of the file. List of available qualities: {c.audio_bitrates}",
    )

    # returns an argparse.Namespace object that stores our argument variables
    return parser.parse_args()


def controller():
    """
    Controls the flow of the program execution.
    """

    args = cli_args()

    #  perform necessary argument validity checks
    if not u.check_cli_args(args.codec, args.bitrate, args.link):
        raise e.LinkError("Invalid Spotify link entered!")

    # i believe getting the link type should be separated from just checking
    # the validity of the link and the audio-related args like codec and bitrate
    if not u.get_link_type(args.link) in c.spotify_link_types:
        raise e.LinkError("Invalid Spotify link type entered!")

    # make the specified dir. if it doesn't exist and open it to store files
    u.directory_maker(args.dir)
    os.chdir(args.dir)

    # grouping all youtube-dl required arguments together before passing them
    # as the controller func parameters
    user_params = {
        "codec": args.codec,
        "quality": args.bitrate,
        "quiet": args.quiet,
    }

    song_download_controller(args.link, user_params)


def song_download_controller(link: str, user_params: dict):
    """
    Handles the control flow for the process to download an individual song.
    """

    # gets the SpotifySong dataclass object to be used for everything else in the func
    song = s.get_song_data(link)

    # use the youtube controller to scrape audio source and download the song
    y.controller(user_params, song)

    # write metadata to the downloaded file
    file_name = (
        f"{u.make_song_title(song.artists, song.name, ', ')}.{user_params['codec']}"
    )

    m.controller(file_name, song, user_params["dir"], user_params["codec"])


def album_download_controller(link: str, user_params: dict, save_dir: str):
    """
    Handles the control flow for the process to download a complete album.
    """

    # todo: we need to make a new directory for the album
    pass
