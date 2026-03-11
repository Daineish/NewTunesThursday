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
