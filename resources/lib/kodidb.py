#!/usr/bin/python

import xbmc
import json
from utils import log_msg, log_exception


class KodiDb:
  @staticmethod
  def SendCommand(method, params=None):
    json_req = {"jsonrpc":"2.0", "method":method, "id":1}
    if params:
      json_req['params'] = params

    r = xbmc.executeJSONRPC(json.dumps(json_req))
    json_rsp = json.loads(r.decode('utf-8', 'replace'))
    if not 'result' in json_rsp:
      log_msg(json_rsp)
      log_msg(json_req)

    return json_rsp

  def videoplaylists(self):
    playlists = self.SendCommand('Files.GetDirectory', {"directory": "special://videoplaylists"})
    if 'result' in playlists and 'files' in playlists['result']:
      return playlists['result']['files']
    return None

  def movies(self):
    movies = self.SendCommand('VideoLibrary.GetMovies')
    if 'result' in movies and 'movies' in movies['result']:
      return movies['result']['movies']
    return None

  def tvshows(self):
    tvshows = self.SendCommand('VideoLibrary.GetTvShows')
    if 'result' in tvshows and 'tvshows' in tvshows['result']:
      return tvshows['result']['tvshows']
    return None

  def musicplaylists(self):
    playlists = self.SendCommand('Files.GetDirectory', {"directory": "special://musicplaylists"})
    if 'result' in playlists and 'files' in playlists['result']:
      return playlists['result']['files']
    return None

  def artists(self):
    artists = self.SendCommand('AudioLibrary.GetArtists', {"albumartistsonly": False})
    if 'result' in artists and 'artists' in artists['result']:
      return artists['result']['artists']
    return None

  def albums(self):
    albums = self.SendCommand('AudioLibrary.GetAlbums')
    if 'result' in albums and 'albums' in albums['result']:
      return albums['result']['albums']
    return None

  def songs(self):
    songs = self.SendCommand('AudioLibrary.GetSongs')
    if 'result' in songs and 'songs' in songs['result']:
      return songs['result']['songs']
    return None

  def genres(self, media_type):
    genres = self.SendCommand('VideoLibrary.GetGenres', {"type":media_type})
    if 'result' in genres and 'genres' in genres['result']:
      return genres['result']['genres']
    return None

  def addons(self):
    all_addons = []
    for addon_type in ['video', 'audio', 'image', 'executable']:
      addons = self.SendCommand('Addons.GetAddons', {"content":addon_type, "properties":["name"]})
      if 'result' in addons and 'addons' in addons['result']:
        all_addons += addons['result']['addons']
    if len(all_addons) > 0:
      return all_addons
    return None
