import datetime
import json


def get_all_usernames(map_file):
    """
    parse all usernames from file
    """
    with open(map_file) as file:
        username_dict = json.loads(file.read())
    return username_dict


def get_track_string(map_file, track, usernames):
    """
    get a formatted string with the information I want from a track.

    Example output (single song):
    Track added by Daine McNiven on March 24:
        "Thinkin Bout You" by Frank Ocean
    """
    time_added = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")
    track_name = track["track"]["name"]
    track_artists = track["track"]["artists"]
    user_added_id = track["added_by"]["id"]
    if user_added_id in usernames:
        user_added = usernames[user_added_id]
    else:
        user_added = "Unknown User"

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
