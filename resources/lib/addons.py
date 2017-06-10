#!/usr/bin/python

from utils import process_method_on_list
from kodidb import KodiDb


class Addons(object):
  def __init__(self, addon, options):
    self.addon = addon
    self.options = options
    self.kodidb = KodiDb()

  def search(self):
    '''search for addons that match a given string'''
    all_items = self.kodidb.addons()
    return process_method_on_list(self.process_addon, all_items)

  def process_addon(self, item):
    '''transform the json received from kodi into something we can use'''
    item['label'] = item['name']
    # abusing this to get at the addon id..
    item['file'] = item['addonid']
    return item
