#!/usr/bin/env python3

import asyncio
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
master_playlist_url = "https://open.spotify.com/playlist/0yeHWhTnNLBKkMG9SowLWt"
weekly_playlist_url = "https://open.spotify.com/playlist/3zxIx3JxIIQTqGIjSM6c8E"

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
    "--masterPlaylistID",
    type=str,
    dest="master_playlist_url",
    default=master_playlist_url,
    help="spotify URL or URI to which we copy to during --action migrate",
)
parser.add_argument(
    "--weeklyPlaylistID",
    type=str,
    dest="weekly_playlist_url",
    default=weekly_playlist_url,
    help="spotify URL or URI of weekly playlist to copy from with --action migrate or to print/message",
)
parser.add_argument(
    "--spotifyUsername",
    type=str,
    dest="spotify_username",
    default="daineish",
    help="your spotify username",
)
parser.add_argument(
    "--facebookCookies",
    type=str,
    dest="fb_cookies_file",
    default="null",
    help="your facebook cookies file",
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
            print(ge_help.get_track_string(args.username_map_file, track))


# Using OAuth now since script now alters playlists
spotify = sp.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))

if args.result_action == "print":
    playlist_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.weekly_playlist_url
    )
    print_tracks(args, playlist_tracks)
elif args.result_action == "message":
    playlist_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.weekly_playlist_url
    )
    asyncio.run(fb_help.message_tracks(args, playlist_tracks))
elif args.result_action == "migrate":
    # Step 1: Copy tracks from weekly playlist to master playlist
    # Step 2: Clear weekly playlist
    prev_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.weekly_playlist_url
    )
    sp_help.add_tracks_to_playlist(spotify, prev_tracks, args.master_playlist_url)
    sp_help.clear_playlist(spotify, prev_tracks, args.weekly_playlist_url)

else:
    sys.exit("Internal error: Unknown action")
