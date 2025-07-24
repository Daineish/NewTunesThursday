#!/usr/bin/env python3

import datetime
import sys
import argparse
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
from helpers import (
    fbchat_helpers as fb_help,
    spotify_helpers as sp_help,
    generic_helpers as ge_help,
)

# Default Playlist
thursday_playlist_url = "https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr"

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
    choices=["message", "print", "migrate"],
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


def print_tracks(args, playlist_tracks):
    """
    prints information from playlist_tracks, with respect to arguments passed in arg
    """
    for track in playlist_tracks:
        time_added = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")

        if time_added > args.start_date:
            print(ge_help.get_track_string(args, track))


# Using OAuth now since script now alters playlists
spotify = sp.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))


if args.result_action == "print":
    playlist_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.playlist_url
    )
    print_tracks(args, playlist_tracks)
elif args.result_action == "message":
    playlist_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.playlist_url
    )
    fb_help.message_tracks(args, playlist_tracks)
elif args.result_action == "migrate":
    # Step 1: Copy tracks from previous playlist to master playlist
    # Step 2: Delete previous playlist (?)
    # Step 3: Create new playlist

    # TODO: Get a better way to get the previous playlist
    #       Current strategy is to use args.date with hardcoded
    #       playlist name. Should be fine since playlists will
    #       only be created/deleted via this script but still hacky
    prev_date_str = args.start_date.strftime("%b %-d, %Y")
    next_date_str = (args.start_date + datetime.timedelta(days=7)).strftime(
        "%b %-d, %Y"
    )
    previous_title = "NTT Weekly " + prev_date_str

    all_playlists = spotify.user_playlists(args.spotify_username, 100)
    found = False
    for cur_playlist in all_playlists["items"]:
        if cur_playlist["name"] == previous_title:
            found = True
            prev_playlist_id = cur_playlist["id"]
            prev_tracks = sp_help.get_playlist_tracks(
                spotify, args.spotify_username, prev_playlist_id
            )

            sp_help.add_tracks_to_playlist(spotify, prev_tracks, args.playlist_url)
            sp_help.create_new_playlist(spotify, args.spotify_username, next_date_str)

    if not found:
        print("Couldn't find previous playlist")
else:
    sys.exit("Internal error: Unknown action")
