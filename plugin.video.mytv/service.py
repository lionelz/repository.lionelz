import http_server
import os
import service_parsers
import shutil
import sys
import time
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


def log(message):
    xbmc.log('MyTV: %s' % message, xbmc.LOGDEBUG)


def get_settings(addon):
    login = addon.getSetting('login')
    password = addon.getSetting('password')
    log('login: %s, password: %s' % (login, password))
    while (login.strip() == '' or password.strip() == ''):
        xbmc.executebuiltin('XBMC.Notification("32010","32011", 10000)')
        result = addon.openSettings()
        login = addon.getSetting('login')
        password = addon.getSetting('password')
        log('login: %s, password: %s' % (login, password))
    return login, password

def addon_enabled(addon_id, enabled):
    json_enabled = ( '{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled",'
        ' "params": { "addonid": "%s", "enabled": %s }}' % (addon_id, enabled))
    xbmc.executeJSONRPC(json_enabled)
    
def iptvsimple_settings(iptvsimple_addon, addon_iptvsimple_path):
    settings_file = os.path.join(addon_iptvsimple_path, 'settings.xml')
    if (not os.path.isfile(settings_file)):
        iptvsimple_addon.setSetting('epgPathType', '0')
    setgs = service_parsers.setting_parser(settings_file)

    setgs['epgCache'] = 'false'
    setgs['epgPath'] = 'http://127.0.0.1:12345/epg.xml'
    setgs['epgPathType'] = '1'
    setgs['epgTSOverride'] = 'false'
    setgs['epgTimeShift'] = '0.000000'
    setgs['epgUrl'] = 'http://127.0.0.1:12345/epg.xml'

    setgs['logoBaseUrl'] = 'http://127.0.0.1:12345/logos'
    setgs['logoFromEpg'] = '0'
    setgs['logoPath'] = 'http://127.0.0.1:12345/logos'
    setgs['logoPathType'] = '1'

    setgs['m3uCache'] = 'false'
    setgs['m3uPath'] = 'http://127.0.0.1:12345/iptv.m3u'
    setgs['m3uPathType'] = '1'
    setgs['m3uUrl'] = 'http://127.0.0.1:12345/iptv.m3u'

    setgs['startNum'] = '1'

    service_parsers.setting_writer(settings_file, setgs)

addon_id = 'plugin.video.mytv'
addon_iptvsimple_id = 'pvr.iptvsimple'
addon_enabled(addon_iptvsimple_id, 'true')
addon = xbmcaddon.Addon(id=addon_id)
iptvsimple_addon = xbmcaddon.Addon(id=addon_iptvsimple_id)

login, password = get_settings(addon)

addon_path = os.path.join(
    xbmc.translatePath('special://masterprofile').decode('utf-8'),
    'addon_data',
    addon_id,
)

addon_iptvsimple_path = os.path.join(
    xbmc.translatePath('special://masterprofile').decode('utf-8'),
    'addon_data',
    addon_iptvsimple_id,
)

log(addon_iptvsimple_path)

myserver = http_server.MyServer(addon_path, login, password)
myserver.start()

iptvsimple_settings(iptvsimple_addon, addon_iptvsimple_path)

time.sleep(5)

addon_enabled(addon_iptvsimple_id, 'false')
addon_enabled(addon_iptvsimple_id, 'true')
