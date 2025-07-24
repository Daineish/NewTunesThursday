# #!/usr/bin/env python3

# import ast
# import datetime
# import sys
# import argparse
# import spotipy as sp
# from numpy import empty
# from getpass import getpass
# from spotipy.oauth2 import SpotifyClientCredentials
# import matplotlib.pyplot as plt
# import numpy as np
# import matplotlib.dates as mdates

# # Default Playlist
# thursday_playlist_url = 'https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr?si=a6eac2bd5ff04567'

# # Usage and argument parsing
# parser = argparse.ArgumentParser(description='This is to be used with our "New Music Thursday" spotify playlist to extract ' +
#                                              'songs and their release date, and plotting this information.')
# parser.add_argument('--date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), dest='start_date', default='2022-01-01',
#                     help='earliest date from which we query songs, format: YYYY-MM-DD')
# parser.add_argument('--spotifyPlaylistID', type=str, dest='playlist_url', default=thursday_playlist_url,
#                     help='spotify URL or URI from which we gather track information')
# parser.add_argument('--spotifyUsername', type=str, dest='spotify_username', default='daineish',
#                     help='your spotify username')

# args = parser.parse_args()


# def get_username(user_id):
#     """
#     parse username from file in args
#     """
#     rv = user_id
#     with open('username_map.dict') as file:
#         username_dict = ast.literal_eval(file.read())
#         if(user_id in username_dict):
#             rv = username_dict[user_id]

#     return rv


# def get_playlist_tracks(username, playlist_id):
#     """
#     get all tracks from a specified playlist using spotify username
#     """
#     results = spotify.user_playlist_tracks(username, playlist_id)
#     tracks = results['items']
#     while results['next']:
#         results = sp.next(results)
#         tracks.extend(results['items'])
#     return tracks


# def get_release_dates(track_list):
#     """
#     parse release date from tracks, return a tuple of lists as follows:
#     [track names], [corresponding release dates]
#     """
#     return [get_username(track['added_by']['id']) for track in track_list[2:]], [track['track']['album']['release_date'] for track in track_list[2:]]


# spotify = sp.Spotify(client_credentials_manager=SpotifyClientCredentials())
# playlist_tracks = get_playlist_tracks(
#     args.spotify_username, args.playlist_url)

# track_names, release_dates = get_release_dates(playlist_tracks)

# # print(track_names)
# # print(release_dates)

# # Choose some nice levels
# levels = np.tile([-5, 5, -3, 3, -1, 1],
#                  int(np.ceil(len(release_dates)/6)))[:len(release_dates)]

# print(levels)

# # Create figure and plot a stem plot with the date
# fig, ax = plt.subplots(figsize=(8.8, 4), constrained_layout=True)
# ax.set(title="Release dates")

# markerline, stemline, baseline = ax.stem(release_dates, levels,
#                                          linefmt="C3-", basefmt="k-",
#                                          use_line_collection=True)

# plt.setp(markerline, mec="k", mfc="w", zorder=3)

# # Shift the markers to the baseline by replacing the y-data by zeros.
# markerline.set_ydata(np.zeros(len(release_dates)))

# # annotate lines
# vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
# for d, l, r, va in zip(release_dates, levels, track_names, vert):
#     ax.annotate(r, xy=(d, l), xytext=(-3, np.sign(l)*3),
#                 textcoords="offset points", va=va, ha="right")

# # format xaxis with 4 month intervals
# # ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=36))
# # ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%b %Y"))
# plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# # remove y axis and spines
# ax.get_yaxis().set_visible(False)
# for spine in ["left", "top", "right"]:
#     ax.spines[spine].set_visible(False)

# ax.margins(y=0.1)
# plt.show()
