#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Tvshows(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for tvshows that match a given string'''
    all_items = self.kodidb.tvshows()
    return process_method_on_list(self.process_tvshow, all_items)

  def process_tvshow(self, item):
    '''transform the json received from kodi into something we can use'''
    return item
