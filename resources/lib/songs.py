#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Songs(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for songs that match a given string'''
    all_items = self.kodidb.songs()
    return process_method_on_list(self.process_song, all_items)

  def process_song(self, item):
    '''transform the json received from kodi into something we can use'''
    # Not the real file -- abusing this to get at the song id
    item['file'] = 'musicdb://songs/%s' % item['songid']
    return item
