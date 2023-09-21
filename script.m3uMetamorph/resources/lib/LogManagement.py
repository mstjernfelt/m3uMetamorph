import xbmc
import xbmcaddon

verbose = False

def debug(message):
    ADDON = xbmcaddon.Addon()
    xbmc.log(f'{ADDON.getAddonInfo("id")} {message}', level=xbmc.LOGDEBUG)

def info(message):
    ADDON = xbmcaddon.Addon()
    xbmc.log(f'{ADDON.getAddonInfo("id")}: {message}', level=xbmc.LOGINFO)

def warning(message):
    ADDON = xbmcaddon.Addon()
    xbmc.log(f'{ADDON.getAddonInfo("id")} {message}', level=xbmc.LOGWARNING)

def error(message):
    ADDON = xbmcaddon.Addon()
    xbmc.log(f'{ADDON.getAddonInfo("id")}: {message}', level=xbmc.LOGERROR)

def critical(message):
    ADDON = xbmcaddon.Addon()    
    xbmc.log(f'{ADDON.getAddonInfo("id")} {message}', level=xbmc.LOGFATAL)