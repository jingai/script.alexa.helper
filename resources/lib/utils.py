#!/usr/bin/python

import xbmc
import xbmcgui
from traceback import format_exc
import sys
import urllib

try:
  from multiprocessing.pool import ThreadPool
  SUPPORTS_POOL = True
except Exception:
  SUPPORTS_POOL = False

ADDON_ID = 'script.alexa.helper'
KODI_LANGUAGE = xbmc.getLanguage(xbmc.ISO_639_1)
if not KODI_LANGUAGE:
  KODI_LANGUAGE = "en"
KODI_VERSION = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])


def log_msg(msg, loglevel=xbmc.LOGDEBUG):
  '''log message to kodi log'''
  if isinstance(msg, unicode):
    msg = msg.encode('utf-8')
  xbmc.log('Alexa Helper --> %s' % msg, level=loglevel)

def log_exception(modulename, exceptiondetails):
  '''helper to properly log an exception'''
  log_msg(format_exc(sys.exc_info()), xbmc.LOGWARNING)
  log_msg('Exception in %s ! --> %s' % (modulename, exceptiondetails), xbmc.LOGERROR)

def process_method_on_list(method_to_run, items):
  '''helper method that processes a method on each listitem with pooling if the system supports it'''
  all_items = []
  if SUPPORTS_POOL:
    pool = ThreadPool()
    try:
      all_items = pool.map(method_to_run, items)
    except Exception:
      # catch exception to prevent threadpool running forever
      log_msg(format_exc(sys.exc_info()))
      log_msg("Error in %s" % method_to_run)
    pool.close()
    pool.join()
  else:
    all_items = [method_to_run(item) for item in items]
    all_items = filter(None, all_items)
  return all_items

def create_listitem(item):
  try:
    liz = xbmcgui.ListItem(label=item.get('label', ''), label2=item.get('label2', ''))
    liz.setPath(item['file'])

    nodetype = 'Video'
    if item['type'] in ['song', 'album', 'artist']:
      nodetype = 'Music'

    infolabels = {}

    # setting the dbtype and dbid is supported from kodi krypton and up
    if KODI_VERSION > 16 and item['type'] not in ['recording', 'channel', 'favourite']:
        infolabels['mediatype'] = item['type']
        # setting the dbid on music items is not supported ?
        if nodetype == 'Video' and 'DBID' in item['extraproperties']:
            infolabels['dbid'] = item['extraproperties']['DBID']

    # assign the infolabels
    liz.setInfo(type=nodetype, infoLabels=infolabels)

    return (item['file'], liz, item.get('isFolder', False))

  except Exception as exc:
    log_exception(__name__, exc)
    log_msg(item)
    return None

def prepare_listitem(item):
  try:
    # fix values returned from json to be used as listitem values
    properties = item.get('extraproperties', {})

    # set type
    for idvar in [
        ('episode', 'DefaultTVShows.png'),
        ('tvshow', 'DefaultTVShows.png'),
        ('movie', 'DefaultMovies.png'),
        ('song', 'DefaultAudio.png'),
        ('album', 'DefaultAudio.png'),
        ('artist', 'DefaultArtist.png'),
        ('musicvideo', 'DefaultMusicVideos.png'),
        ('recording', 'DefaultTVShows.png'),
        ('channel', 'DefaultAddonPVRClient.png')]:
      dbid = item.get(idvar[0] + 'id')
      if dbid:
        properties['DBID'] = str(dbid)
        if not item.get('type'):
          item['type'] = idvar[0]
        break

    properties['dbtype'] = item['type']
    properties['DBTYPE'] = item['type']
    properties['type'] = item['type']
    properties['path'] = item.get('file')

    item['extraproperties'] = properties

    if 'file' not in item:
      item['file'] = ''

    # return the result
    return item

  except Exception as exc:
      log_exception(__name__, exc)
      log_msg(item)
      return None
