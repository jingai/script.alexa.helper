#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Movies(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for movies that match a given string'''
    all_items = self.kodidb.movies()
    return process_method_on_list(self.process_movie, all_items)

  def process_movie(self, item):
    '''transform the json received from kodi into something we can use'''
    return item
