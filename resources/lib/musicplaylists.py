#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Musicplaylists(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for musicplaylists that match a given string'''
    all_items = self.kodidb.musicplaylists()
    return process_method_on_list(self.process_musicplaylist, all_items)

  def process_musicplaylist(self, item):
    '''transform the json received from kodi into something we can use'''
    return item
