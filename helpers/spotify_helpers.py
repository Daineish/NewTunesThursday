import ast
import datetime


def get_playlist_tracks(spotify, username, playlist_id):
    """
    get all tracks from a specified playlist using spotify username
    calls spotify API
    """
    results = spotify.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    return tracks


def add_tracks_to_playlist(spotify, tracks, playlist_id):
    """
    add tracks to already-existing playlist
    calls spotify API
    """
    track_ids = [x["track"]["uri"] for x in tracks]
    spotify.playlist_add_items(playlist_id, track_ids)


def clear_playlist(spotify, tracks, playlist_id):
    """
    clear all 'tracks' from a 'playlist_id'
    calls spotify API
    """
    track_ids = [x["track"]["uri"] for x in tracks]
    spotify.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)


def create_new_playlist(
    spotify, username, date, title="NTT Weekly ", desc="New Tunes Thursday Weekly "
):
    """
    create a new spotify playlist titled 'title' + date
    calls spotify API
    """
    playlist_title = title + date
    playlist_desc = desc + date

    return spotify.user_playlist_create(username, playlist_title, True, playlist_desc)
