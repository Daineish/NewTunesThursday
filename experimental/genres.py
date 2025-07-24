#!/usr/bin/env python3

import ast
import datetime
import sys
import fbchat
import argparse
import spotipy as sp
from numpy import empty
from getpass import getpass
from spotipy.oauth2 import SpotifyClientCredentials

# Default Playlist
thursday_playlist_url = (
    "https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr?si=a6eac2bd5ff04567"
)

# Usage and argument parsing
parser = argparse.ArgumentParser(
    description='This is to be used with our "New Music Thursday" spotify playlist to extract recently '
    + "added songs and send them to a facebook messenger chat."
)
parser.add_argument(
    "--date",
    type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
    dest="start_date",
    default="2022-01-01",
    help="earliest date from which we query songs, format: YYYY-MM-DD",
)
parser.add_argument(
    "--action",
    choices=["message", "print"],
    dest="result_action",
    default="print",
    help="action which to take with results, either message group or print the restults",
)
parser.add_argument(
    "--messageID",
    type=str,
    dest="messengerID",
    default="null",
    help="FB messenger chat uid",
)
parser.add_argument(
    "--spotifyPlaylistID",
    type=str,
    dest="playlist_url",
    default=thursday_playlist_url,
    help="spotify URL or URI from which we gather track information",
)
parser.add_argument(
    "--spotifyUsername",
    type=str,
    dest="spotify_username",
    default="daineish",
    help="your spotify username",
)
parser.add_argument(
    "--facebookEmail",
    type=str,
    dest="fb_email",
    default="null",
    help="your facebook email, when using the message action, this will be the account from which you send the message",
)
parser.add_argument(
    "--usernameMapFile",
    type=str,
    dest="username_map_file",
    default="username_map.dict",
    help="a file mapping usernames to actual names of people for printing",
)

args = parser.parse_args()


def get_playlist_tracks(username, playlist_id):
    """
    get all tracks from a specified playlist using spotify username
    """
    results = spotify.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    return tracks


def get_username(args, user_id):
    """
    parse username from file in args
    """
    rv = user_id
    with open(args.username_map_file) as file:
        username_dict = ast.literal_eval(file.read())
        if user_id in username_dict:
            rv = username_dict[user_id]

    return rv


def get_track_string(args, track):
    """
    get a formatted string with the information I want from a track.

    Example output (single song):
    Track added by Daine McNiven on March 24:
        "Thinkin Bout You" by Frank Ocean
    """
    user_added = get_username(args, track["added_by"]["id"])

    time_added = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")
    track_name = track["track"]["name"]
    track_artists = track["track"]["artists"]
    user_added_id = track["added_by"]["id"]
    user_added = get_username(args, user_added_id)

    artists_string = ""
    for artist in track_artists[:-1]:
        if artists_string != "":
            artists_string += ", "
        artists_string += artist["name"]
    if artists_string != "":
        artists_string += " and " + track_artists[-1]["name"]
    else:
        artists_string = track_artists[0]["name"]
    ret_str = (
        "Track added by " + user_added + " on " + time_added.strftime("%B %d") + ":\n"
    )
    ret_str += '\t"' + track_name + '" by ' + artists_string + "\n"
    return ret_str


spotify = sp.Spotify(client_credentials_manager=SpotifyClientCredentials())
playlist_tracks = get_playlist_tracks(args.spotify_username, args.playlist_url)

main_artists = [track["track"]["artists"][0] for track in playlist_tracks]
main_genres = []
for artist in main_artists:
    cur_art = spotify.artist(artist["id"])
    if len(cur_art["genres"]) > 0:  # is not empty):
        # print(artist['name'], ' genre is: ', cur_art['genres'][0], '\n')
        main_genres += [cur_art["genres"][0]]

print(main_genres)
