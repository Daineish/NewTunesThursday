import fbchat
from getpass import getpass
import datetime
from helpers import generic_helpers

# IMPORTANT NOTE: There's a bug in fbchat which was giving me an index error while trying to log in.
#                 I was able to fix this by changing a line in _state.py in the library. See
#                 https://github.com/fbchat-dev/fbchat/issues/615#issuecomment-710673863 for
#                 the change that worked for me.


def message_tracks(args, playlist_tracks):
    """
    messages a fb chat with info from playlist_tracks, with respect to arguments passed in arg
    """
    if not playlist_tracks:
        return

    print("Attempting to log in to facebook.")
    if args.fb_email == "null":
        fb_username = input("Facebook email: ")
    else:
        fb_username = args.fb_email
    fb_client = fbchat.Client(fb_username, getpass())

    # get group message ID
    if args.messengerID == "null":
        groupchat_uid = input("groupchat uid: ")
    else:
        groupchat_uid = args.messengerID

    # send header message to group
    msg = "-" * 20 + "\nSongs added on or after " + args.start_date.strftime("%B %d")
    sent = fb_client.send(
        fbchat.Message(text=msg),
        thread_id=groupchat_uid,
        thread_type=fbchat.ThreadType.GROUP,
    )

    # send message for each track in list
    for track in playlist_tracks:
        time_added = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")

        if time_added > args.start_date:
            msg = generic_helpers.get_track_string(args, track)
            sent = fb_client.send(
                fbchat.Message(text=msg),
                thread_id=groupchat_uid,
                thread_type=fbchat.ThreadType.GROUP,
            )

    # send footer message to group
    msg = "-" * 20
    sent = fb_client.send(
        fbchat.Message(text=msg),
        thread_id=groupchat_uid,
        thread_type=fbchat.ThreadType.GROUP,
    )

    # fb_client.logout() # broken idk
