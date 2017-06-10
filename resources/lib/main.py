#!/usr/bin/python

import sys
import os
import re
import unicodedata
import codecs
import urlparse
import xbmc
import xbmcplugin
import xbmcaddon
from utils import log_msg, log_exception, ADDON_ID, KODI_LANGUAGE
from utils import process_method_on_list, prepare_listitem, create_listitem
from roman import toRoman
from num2words import num2words
from fuzzywuzzy import fuzz, process

ADDON_HANDLE = int(sys.argv[1])


# NOTE: this is also in Kodi-Voice!
def sanitize_name(media_name, normalize=True):
  if normalize:
    try:
      # Normalize string
      name = unicodedata.normalize('NFKD', media_name).encode('ASCII', 'ignore')
    except:
      name = media_name
  else:
    name = media_name

  # Remove invalid characters, per Amazon:
  # Slot type values can contain alphanumeric characters, spaces, commas,
  # apostrophes, periods, hyphens, ampersands and the @ symbol only.
  name = re.sub(r'[`~!#$%^*()_=+\[\]{}\\|;:"<>/?]', '', name)

  # Slot items cannot exceed 140 chars, per Amazon
  if len(name) > 140:
    name = name[:140].rsplit(' ', 1)[0]

  name = name.strip()
  return name

# Replace digits with word-form numbers.
def digits2words(phrase, lang='en'):
  wordified = ''
  for word in phrase.split():
    if word.isnumeric():
      word = num2words(float(word), lang=lang)
    wordified = wordified + word + " "
  return wordified[:-1]

# Replace word-form numbers with digits.
def words2digits(phrase, lang='en'):
  numwords = {}

  numwords_file = os.path.join(os.path.dirname(__file__), "NUMWORDS." + lang + ".txt")
  f = codecs.open(numwords_file, 'rb', 'utf-8')
  for line in f:
    l = line.encode("utf-8").strip().split('|')
    if l[0] == 'connectors':
      connectors = l[1:]
      for words in connectors:
        for word in words.strip().split():
          numwords[word.decode('utf-8')] = (1, 0, 0)
    if l[0] == 'units':
      units = l[1:]
      for idx, words in enumerate(units):
        for word in words.strip().split():
          numwords[word.decode('utf-8')] = (1, idx, 1)
    if l[0] == 'tens':
      tens = l[1:]
      for idx, words in enumerate(tens):
        for word in words.strip().split():
          numwords[word.decode('utf-8')] = (1, idx * 10, 2)
    if l[0] == 'scales':
      scales = l[1:]
      for idx, words in enumerate(scales):
        for word in words.strip().split():
          numwords[word.decode('utf-8')] = (10 ** (idx * 3 or 2), 0, 3)
  f.close()

  wordified = ''
  current = result = 0
  prev_level = sys.maxint
  in_number = False
  phrase = re.sub(r'[-]', ' ', phrase)
  for word in phrase.split():
    if word not in numwords:
      if in_number:
        wordified = wordified + str(current + result) + " "
        current = result = 0
        prev_level = sys.maxint
      in_number = False
      wordified = wordified + word + " "
    else:
      in_number = True
      scale, increment, level = numwords[word]

      # Handle things like "nine o two one o" (9 0 2 1 0)
      if level == prev_level == 1:
        wordified = wordified + str(current) + " "
        current = result = 0

      prev_level = level

      # account for things like "hundred fifty" vs "one hundred fifty"
      if scale >= 100 and current == 0:
        current = 1

      current = current * scale + increment
      if scale > 100:
        result += current
        current = 0

  if in_number:
    wordified = wordified + str(current + result) + " "

  return wordified[:-1]

# Replace digits with roman numerals.
def digits2roman(phrase, lang='en'):
  wordified = ''
  for word in phrase.split():
    if word.isnumeric():
      word = toRoman(int(word))
    wordified = wordified + word + " "
  return wordified[:-1]

# Replace word-form numbers with roman numerals.
def words2roman(phrase, lang='en'):
  return digits2roman(words2digits(phrase, lang=lang), lang=lang)

# Match heard string to something in the results
def matchHeard(heard, results, lookingFor='label'):
  located = []

  heard_lower = heard.lower()

  # Very ugly hack for German Alexa.  In English, if a user specifies
  # 'percent', she converts it to a '%' symbol.  In German, for whatever
  # reason, she leaves it unconverted as 'prozent'.  Let's convert here.
  heard_lower = re.sub(r'prozent(?=[.,\s]|$)', '%', heard_lower)

  log_msg('Trying to match: %s' % (heard_lower.encode("utf-8")), xbmc.LOGNOTICE)

  heard_ascii = sanitize_name(heard_lower)
  for result in results:
    result_lower = result[lookingFor].lower()

    # Direct comparison
    if type(heard_lower) is type(result_lower):
      if result_lower == heard_lower:
        log_msg('Simple match on direct comparison', xbmc.LOGNOTICE)
        located = [result]
        break

    # Strip out non-ascii symbols
    result_name = sanitize_name(result_lower)

    # Direct comparison (ASCII)
    if result_name == heard_ascii:
      log_msg('Simple match on direct comparison (ASCII)', xbmc.LOGNOTICE)
      located = [result]
      break

  if len(located) == 0:
    log_msg('Simple match failed, trying fuzzy match...', xbmc.LOGNOTICE)

    fuzzy_results = []
    for f in (None, digits2roman, words2roman, words2digits, digits2words):
      try:
        if f is not None:
          ms = f(heard_lower, KODI_LANGUAGE)
          mf = f.__name__
        else:
          ms = heard_lower
          mf = 'heard'

        log_msg('  %s: "%s"' % (mf, ms.encode("utf-8")), xbmc.LOGNOTICE)

        rv = process.extract(ms, [d[lookingFor] for d in results], limit=1, scorer=fuzz.QRatio)
        if rv[0][1] >= 75:
          fuzzy_results.append(rv[0])
          log_msg('   -- Score %d%%' % (rv[0][1]), xbmc.LOGNOTICE)
          if rv[0][1] == 95:
            # Let's consider a 95% match 'good enough'
            break
        else:
          log_msg('  -- Score %d%% too low for "%s"' % (rv[0][1], rv[0][0].encode("utf-8")), xbmc.LOGNOTICE)
      except:
        continue

    # Got a match?
    if len(fuzzy_results) > 0:
      winner = sorted(fuzzy_results, key=lambda x: x[1], reverse=True)[0]
      log_msg('  WINNER: "%s" @ %d%%' % (winner[0].encode("utf-8"), winner[1]), xbmc.LOGNOTICE)
      located = [(item for item in results if item[lookingFor] == winner[0]).next()]

  return located

class Main(object):
  def __init__(self):
    self.addon = xbmcaddon.Addon(ADDON_ID)
    self.options = self.get_options()
    self.mainlisting()
    self.close()

  def close(self):
    '''Cleanup Kodi Cpython instances'''
    del self.addon
    log_msg("MainModule exited")

  def get_options(self):
    '''get the options provided to the plugin path'''

    options = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '').lower().decode("utf-8")))
    return options

  def mainlisting(self):
    '''display the listing for the provided action and mediatype'''
    media_type = self.options['mediatype']
    action = self.options['action']
    # set widget content type
    xbmcplugin.setContent(ADDON_HANDLE, media_type)

    # call the correct method to get the content from json
    all_items = []
    log_msg('MEDIATYPE: %s - ACTION: %s -- querying kodi api to get items' % (media_type, action))

    # dynamically import and load the correct module, class and function
    try:
      media_module = __import__(media_type)
      media_class = getattr(media_module, media_type.capitalize())(self.addon, self.options)
      all_items = getattr(media_class, action)()
      del media_class
    except AttributeError:
      log_exception(__name__, 'Incorrect action or type called')
    except Exception as exc:
      log_exception(__name__, exc)

    matched_items = matchHeard(self.options['mediatitle'], all_items)
    if len(matched_items) > 0:
      # prepare listitems
      matched_items = process_method_on_list(prepare_listitem, matched_items)

      # fill that listing...
      xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
      matched_items = process_method_on_list(create_listitem, matched_items)
      xbmcplugin.addDirectoryItems(ADDON_HANDLE, matched_items, len(matched_items))

    # end directory listing
    xbmcplugin.endOfDirectory(handle=ADDON_HANDLE)
