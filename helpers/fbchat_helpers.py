from fbchat_muqit import Client, ThreadType
from getpass import getpass
import datetime
from helpers import generic_helpers


async def message_tracks(args, playlist_tracks):
    """
    messages a fb chat with info from playlist_tracks, with respect to arguments passed in arg
    """
    if not playlist_tracks:
        return

    # get group message ID
    if args.messengerID == "null":
        groupchat_uid = input("groupchat uid: ")
    else:
        groupchat_uid = args.messengerID

    bot = await Client.startSession(args.fb_cookies_file)

    if await bot.isLoggedIn():
        # send header message to group
        msg = "-" * 20

        await bot.sendMessage(msg, groupchat_uid, ThreadType.GROUP)

        # Don't really need this anymore with new system, could just do entire weekly playlist
        for track in playlist_tracks:
            time_added = datetime.datetime.strptime(
                track["added_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

            if time_added > args.start_date:
                msg = generic_helpers.get_track_string(args.username_map_file, track)
                await bot.sendMessage(msg, groupchat_uid, ThreadType.GROUP)

        # send footer message to group
        msg = "-" * 20
        await bot.sendMessage(msg, groupchat_uid, ThreadType.GROUP)
