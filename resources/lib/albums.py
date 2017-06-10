#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Albums(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for albums that match a given string'''
    if 'artistid' in self.options:
      all_items = self.kodidb.albums(self.options['artistid'])
    else:
      all_items = self.kodidb.albums()
    return process_method_on_list(self.process_album, all_items)

  def process_album(self, item):
    '''transform the json received from kodi into something we can use'''
    item['file'] = 'musicdb://albums/%s' % item['albumid']
    item['isFolder'] = True
    return item
