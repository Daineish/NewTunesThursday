import time
import jwt
import requests


def generate_developer_token(team_id, key_id, private_key):
    """
    Generate a short-lived Apple Music developer token (JWT).
    private_key should be the contents of the .p8 file as a string.
    """
    now = int(time.time())
    headers = {"alg": "ES256", "kid": key_id}
    payload = {
        "iss": team_id,
        "iat": now,
        "exp": now + 43200,  # 12 hours
    }
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def get_user_storefront(developer_token, user_token):
    """
    Returns the two-letter storefront code for the authenticated user (e.g. "ca", "us").
    """
    headers = {
        "Authorization": f"Bearer {developer_token}",
        "Music-User-Token": user_token,
    }
    response = requests.get("https://api.music.apple.com/v1/me/storefront", headers=headers)
    response.raise_for_status()
    return response.json()["data"][0]["id"]


def search_track(developer_token, track_name, artist_name, storefront="us"):
    """
    Search the Apple Music catalog for a track by name and artist.
    Returns the Apple Music song ID, or None if not found.
    """
    url = f"https://api.music.apple.com/v1/catalog/{storefront}/search"
    headers = {"Authorization": f"Bearer {developer_token}"}
    params = {"term": f"{track_name} {artist_name}", "types": "songs", "limit": 1}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    songs = response.json().get("results", {}).get("songs", {}).get("data", [])
    if songs:
        return songs[0]["id"]
    return None


def get_or_create_folder(developer_token, user_token, folder_name):
    """
    Find an existing top-level Apple Music library folder by name, or create it.
    Returns the folder ID.
    """
    auth_headers = {
        "Authorization": f"Bearer {developer_token}",
        "Music-User-Token": user_token,
    }

    # Fetch top-level library items (playlists + folders)
    url = "https://api.music.apple.com/v1/me/library/playlist-folders/p.playlistsroot/children"
    while url:
        response = requests.get(url, headers=auth_headers)
        response.raise_for_status()
        data = response.json()
        for item in data.get("data", []):
            if (
                item["type"] == "library-playlist-folders"
                and item["attributes"]["name"] == folder_name
            ):
                return item["id"]
        url = data.get("next")

    # Not found — create it
    response = requests.post(
        "https://api.music.apple.com/v1/me/library/playlist-folders",
        headers=auth_headers,
        json={"attributes": {"name": folder_name}},
    )
    response.raise_for_status()
    return response.json()["data"][0]["id"]


def create_playlist(developer_token, user_token, name, description="", folder_id=None):
    """
    Create a new playlist in the user's Apple Music library.
    Optionally place it inside a folder by passing folder_id.
    Returns the new playlist's ID.
    """
    url = "https://api.music.apple.com/v1/me/library/playlists"
    headers = {
        "Authorization": f"Bearer {developer_token}",
        "Music-User-Token": user_token,
    }
    body = {"attributes": {"name": name, "description": description}}
    if folder_id:
        body["relationships"] = {
            "parent": {"data": [{"id": folder_id, "type": "library-playlist-folders"}]}
        }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    return response.json()["data"][0]["id"]


def add_tracks_to_playlist(developer_token, user_token, playlist_id, track_ids):
    """
    Add a list of Apple Music song IDs to a library playlist.
    """
    url = f"https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {developer_token}",
        "Music-User-Token": user_token,
    }
    body = {"data": [{"id": tid, "type": "songs"} for tid in track_ids]}

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()


def mirror_spotify_tracks_to_apple_music(
    spotify_tracks,
    developer_token,
    user_token,
    playlist_name,
    storefront="us",
    folder_name=None,
):
    """
    Given a list of Spotify track objects, search for each on Apple Music,
    create a new Apple Music playlist, and populate it with the found tracks.
    Optionally place the playlist inside a library folder (created if it doesn't exist).

    Returns (playlist_id, found_count, not_found_count).
    """
    if storefront == "us":
        storefront = get_user_storefront(developer_token, user_token)
        print(f"Using storefront: {storefront}")

    folder_id = None
    if folder_name:
        print(f"Locating Apple Music folder: {folder_name}")
        folder_id = get_or_create_folder(developer_token, user_token, folder_name)

    print(f"Creating Apple Music playlist: {playlist_name}")
    playlist_id = create_playlist(
        developer_token, user_token, playlist_name, folder_id=folder_id
    )

    apple_ids = []
    not_found = []

    for item in spotify_tracks:
        track = item["track"]
        name = track["name"]
        artist = track["artists"][0]["name"]

        apple_id = search_track(developer_token, name, artist, storefront)
        if apple_id:
            apple_ids.append(apple_id)
        else:
            not_found.append(f'"{name}" by {artist}')

    if apple_ids:
        add_tracks_to_playlist(developer_token, user_token, playlist_id, apple_ids)

    if not_found:
        print(f"  {len(not_found)} track(s) not found on Apple Music:")
        for t in not_found:
            print(f"    - {t}")

    for t in apple_ids:
        print(f"  Found track ID {t} on Apple Music")

    print(
        f"  Added {len(apple_ids)}/{len(spotify_tracks)} tracks to Apple Music playlist."
    )
    return playlist_id, len(apple_ids), len(not_found)
