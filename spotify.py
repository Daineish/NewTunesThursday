#!/usr/bin/env python3

import datetime
import string
import sys
from xmlrpc.client import DateTime
from numpy import empty
import spotipy as sp
import fbchat
from getpass import getpass
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
import argparse

# Default Playlist
thursday_playlist_url = 'https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr?si=a6eac2bd5ff04567'

# Usage and argument parsing
parser = argparse.ArgumentParser(description='This is to be used with our "New Music Thursday" spotify playlist to extract recently ' +
                                             'added songs and send them to a facebook messenger chat.')
parser.add_argument('--date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), dest='start_date', default='2022-01-01',
                    help='earliest date from which we query songs, format: YYYY-MM-DD')
parser.add_argument('--action', choices=['message', 'print'], dest='result_action', default='print',
                    help='action which to take with results, either message group or print the restults')
parser.add_argument('--messageID', type=str, dest='messengerID', default='null',
                    help='FB messenger chat uid')
parser.add_argument('--spotifyPlaylistID', type=str, dest='playlist_url', default=thursday_playlist_url,
                    help='spotify URL or URI from which we gather track information')
parser.add_argument('--spotifyUsername', type=str, dest='spotify_username', default='daineish',
                    help='your spotify username')
parser.add_argument('--facebookEmail', type=str, dest='fb_email', default='null',
                    help='your facebook email, when using the message action, this will be the account from which you send the message')

args = parser.parse_args()


def get_playlist_tracks(username, playlist_id):
    """
    get all tracks from a specified playlist using spotify username
    """
    results = spotify.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def get_track_string(track):
    """
    get a formatted string with the information I want from a track.

    Example output (single song):
    Track added by daineish on March 24:
        "Thinkin Bout You" by Frank Ocean
    """
    time_added = datetime.datetime.strptime(
        track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
    user_added = track['added_by']['id']
    track_name = track['track']['name']
    track_artists = track['track']['artists']
    artists_string = ""
    for artist in track_artists[:-1]:
        if(artists_string is not ""):
            artists_string += ', '
        artists_string += artist['name']
    if(artists_string is not ""):
        artists_string += ' and ' + track_artists[-1]['name']
    else:
        artists_string = track_artists[0]['name']
    ret_str = "Track added by " + user_added + \
        " on " + time_added.strftime('%B %d') + ":\n"
    ret_str += "\t\"" + track_name + "\" by " + artists_string + "\n"
    return ret_str


def print_tracks(args, playlist_tracks):
    """
    prints information from playlist_tracks, with respect to arguments passed in arg
    """
    for track in playlist_tracks:
        time_added = datetime.datetime.strptime(
            track['added_at'], '%Y-%m-%dT%H:%M:%SZ')

        if(time_added > args.start_date):
            print(get_track_string(track))


def message_tracks(args, playlist_tracks):
    """
    messages a fb chat with info from playlist_tracks, with respect to arguments passed in arg
    """
    if(playlist_tracks is empty):
        return

    print("Attempting to log in to facebook.")
    if(args.fb_email == 'null'):
        fb_username = input("Facebook email: ")
    else:
        fb_username = args.fb_email
    fb_client = fbchat.Client(fb_username, getpass())

    if(args.messengerID == 'null'):
        groupchat_uid = input("groupchat uid: ")
    else:
        groupchat_uid = args.messengerID

    msg = "-" * 20 + \
        "\nSongs added on or after " + args.start_date.strftime('%B %d')
    sent = fb_client.send(fbchat.Message(text=msg),
                          thread_id=groupchat_uid, thread_type=fbchat.ThreadType.GROUP)

    for track in playlist_tracks:
        time_added = datetime.datetime.strptime(
            track['added_at'], '%Y-%m-%dT%H:%M:%SZ')

        if(time_added > args.start_date):
            msg = get_track_string(track)
            sent = fb_client.send(fbchat.Message(text=msg),
                                  thread_id=groupchat_uid, thread_type=fbchat.ThreadType.GROUP)

    msg = "-" * 20
    sent = fb_client.send(fbchat.Message(text=msg),
                          thread_id=groupchat_uid, thread_type=fbchat.ThreadType.GROUP)

    # fb_client.logout() # broken idk


spotify = sp.Spotify(client_credentials_manager=SpotifyClientCredentials())
playlist_tracks = get_playlist_tracks(
    args.spotify_username, args.playlist_url)

if(args.result_action == 'print'):
    print_tracks(args, playlist_tracks)
elif(args.result_action == 'message'):
    # IMPORTANT NOTE: There's a bug in fbchat which was giving me an index error while trying to log in.
    #                 I was able to fix this by changing a line in _state.py in the library. See
    #                 https://github.com/fbchat-dev/fbchat/issues/615#issuecomment-710673863 for
    #                 the change that worked for me.
    message_tracks(args, playlist_tracks)
