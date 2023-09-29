# -*- coding: utf-8 -*-

import sys
import xbmc
import logging
import xbmcvfs
import xbmcaddon

PY3 = sys.version_info.major >= 3

if PY3:
    def translate(text):
        return ADDON.getLocalizedString(text)

    def encode(s):
        return s.encode("utf-8")

    def decode(s):
        return s.decode("utf-8")

    def str_to_unicode(s):
        return s

else:
    def translate(text):
        return ADDON.getLocalizedString(text).encode("utf-8")

    def encode(s):
        return s

    def decode(s):
        return s

    def str_to_unicode(s):
        return s.decode("utf-8")

ADDON = xbmcaddon.Addon()
ADDON_PATH = str_to_unicode(ADDON.getAddonInfo("path"))
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_ID = ADDON.getAddonInfo("id")

def get_movie_output_path():
    output_path = get_setting("movie_output_path")
    output_path = output_path.rstrip('/')
    output_path = output_path.rstrip('\\')

    output_path = f"{output_path}/{get_provider_name()}/"

    return output_path

def get_series_output_path():
    output_path = get_setting("series_output_path")
    output_path = output_path.rstrip('/')
    output_path = output_path.rstrip('\\')

    output_path = f"{output_path}/{get_provider_name()}/"

    return output_path

def get_tv_output_path():
    output_path = get_setting("tv_output_path")
    tv_output_filename = get_setting("tv_output_filename")
    output_path = output_path.rstrip('/')
    output_path = output_path.rstrip('\\')

    output_path = f"{output_path}/{get_provider_name()}/"
    output_path = os.path.join(output_path, tv_output_filename)
    return output_path

def get_playlist_path():
    home = xbmcvfs.translatePath('special://home')
    playlist_path = f"{home}{get_provider_name()}/playlist.m3u"

    return playlist_path

def get_xmltv_path():
    home = xbmcvfs.translatePath('special://home')
    playlist_path = f"{home}{get_provider_name()}xmltv.xml"

    return playlist_path

def get_tv_m3u_path():
    home = xbmcvfs.translatePath('special://home')
    tv_m3u_path = f"{home}xmltv.m3u"

    return tv_m3u_path

def get_group_json_path():
    home = xbmcvfs.translatePath('special://home')
    group_json_path = f"{home}{get_provider_name()}/groups.json"

    return group_json_path

def get_playlist_url():
    playlist_url = get_setting("playlist_url")

    return playlist_url

def get_xmltv_url():
    xmltv_url = get_setting("xmltv_url")

    return xmltv_url

def get_provider_name():
    provider_name = get_setting("provider_name")

    return provider_name

def get_setting(setting):
    return ADDON.getSetting(setting)


def get_boolean_setting(setting):
    return get_setting(setting) == "true"


def get_int_setting(setting):
    return int(get_setting(setting))


def open_settings():
    ADDON.openSettings()


def get_inverted():
    return get_boolean_setting("invert")


def get_lines():
    nr_lines = get_setting("lines")
    if nr_lines == "1":
        return 100
    elif nr_lines == "2":
        return 50
    elif nr_lines == "3":
        return 20
    else:
        return 0


def is_default_window():
    return not get_boolean_setting("custom_window")


def parse_exceptions_only():
    return get_boolean_setting("exceptions_only")

class KodiLogHandler(logging.StreamHandler):
    levels = {
        logging.CRITICAL: xbmc.LOGFATAL,
        logging.ERROR: xbmc.LOGERROR,
        logging.WARNING: xbmc.LOGWARNING,
        logging.INFO: xbmc.LOGINFO,
        logging.DEBUG: xbmc.LOGDEBUG,
        logging.NOTSET: xbmc.LOGNONE,
    }

    def __init__(self):
        super(KodiLogHandler, self).__init__()
        self.setFormatter(logging.Formatter("[{}] %(message)s".format(ADDON_ID)))

    def emit(self, record):
        xbmc.log(self.format(record), self.levels[record.levelno])

    def flush(self):
        pass


def set_logger(name=None, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.addHandler(KodiLogHandler())
    logger.setLevel(level)

import os

def create_directory(directory_path):
    try:
        os.mkdir(directory_path)
        print("Directory created successfully.")
    except FileExistsError:
        print("Directory already exists.")