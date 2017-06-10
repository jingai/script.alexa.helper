#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Moviegenres(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for movie genres that match a given string'''
    all_items = self.kodidb.genres('movie')
    return process_method_on_list(self.process_moviegenre, all_items)

  def process_moviegenre(self, item):
    '''transform the json received from kodi into something we can use'''
    item['type'] = 'unknown'
    return item
