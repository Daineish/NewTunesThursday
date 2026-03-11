#!/usr/bin/env python3

import asyncio
import datetime
import os
import sys

import argparse
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
from helpers import (
    spotify_helpers as sp_help,
    generic_helpers as ge_help,
    apple_music_helpers as am_help,
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
    default=datetime.datetime.strptime("2022-01-01", "%Y-%m-%d"),
    help="earliest date from which we query songs, format: YYYY-MM-DD",
)
parser.add_argument(
    "--action",
    choices=["message", "print", "migrate", "apple"],
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
    usernames = ge_help.get_all_usernames(args.username_map_file)
    for track in playlist_tracks:
        time_added = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")

        if time_added > args.start_date:
            print(ge_help.get_track_string(args.username_map_file, track, usernames))


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

    # Double check that we want to send #x songs
    num_tracks = len(playlist_tracks)
    answer = input(f"Are you sure you want to send {num_tracks} songs?").strip().lower()
    if answer != "yes" and answer != "y":
        sys.exit("User aborted")

    from helpers import fbchat_helpers as fb_help

    asyncio.run(fb_help.message_tracks(args, playlist_tracks))
elif args.result_action == "migrate":
    # Step 1: Copy tracks from weekly playlist to master playlist
    # Step 2: Clear weekly playlist
    prev_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.weekly_playlist_url
    )
    sp_help.add_tracks_to_playlist(spotify, prev_tracks, args.master_playlist_url)
    sp_help.clear_playlist(spotify, prev_tracks, args.weekly_playlist_url)

elif args.result_action == "apple":
    # Fetch the weekly playlist and mirror it to a new Apple Music playlist
    playlist_tracks = sp_help.get_playlist_tracks(
        spotify, args.spotify_username, args.weekly_playlist_url
    )

    apple_team_id = os.environ.get("APPLE_TEAM_ID")
    apple_key_id = os.environ.get("APPLE_KEY_ID")
    apple_private_key = os.environ.get("APPLE_PRIVATE_KEY")
    apple_user_token = os.environ.get("APPLE_MUSIC_USER_TOKEN")

    if not all([apple_team_id, apple_key_id, apple_private_key, apple_user_token]):
        sys.exit(
            "Error: Apple Music credentials not set. "
            "Set APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY, and APPLE_MUSIC_USER_TOKEN."
        )

    if not playlist_tracks:
        print("Weekly playlist is empty, skipping Apple Music sync.")
        sys.exit(0)

    dev_token = am_help.generate_developer_token(
        apple_team_id, apple_key_id, apple_private_key
    )
    now = datetime.datetime.now()
    last_thursday = now - datetime.timedelta(days=(now.weekday() - 3) % 7)
    playlist_name = "New Music Thursday " + last_thursday.strftime("%b %-d")
    folder_name = "New Music Thursday " + str(last_thursday.year)
    am_help.mirror_spotify_tracks_to_apple_music(
        playlist_tracks,
        dev_token,
        apple_user_token,
        playlist_name,
        folder_name=folder_name,
    )

else:
    sys.exit("Internal error: Unknown action")
