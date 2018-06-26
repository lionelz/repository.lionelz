import http_server
import os
import service_parsers
import shutil
import sys
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


def log(message):
    xbmc.log('MyTV: %s' % message, xbmc.LOGDEBUG)


def get_settings(addon):
    login = addon.getSetting('login')
    password = addon.getSetting('password')
    language = addon.getLocalizedString
    log('login: %s, password: %s' % (login, password))
    while (login.strip() == '' or password.strip() == ''):
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", 10000)' %
            (language(32010), language(32011)))
        result = addon.openSettings()
        login = addon.getSetting('login')
        password = addon.getSetting('password')
        log('login: %s, password: %s' % (login, password))
    return login, password

def addon_enabled(addon_id, enabled):
    json_enabled = ( '{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled",'
        ' "params": { "addonid": "%s", "enabled": %s }}' % (addon_id, enabled))
    xbmc.executeJSONRPC(json_enabled)
    
def iptvsimple_settings(addon_iptvsimple_path):
    settings_file = os.path.join(addon_iptvsimple_path, 'settings.xml')
    if os.path.exists(settings_file):
        setgs = service_parsers.setting_parser(settings_file)
    else:
        if not os.path.exists(addon_iptvsimple_path):
            os.makedirs(addon_iptvsimple_path)
        setgs = {}

    setgs['epgCache'] = 'false'
    setgs['epgTSOverride'] = 'false'
    setgs['epgTimeShift'] = '0.0000'
    setgs['epgPathType'] = '1'
    setgs['epgUrl'] = 'http://127.0.0.1:12345/epg.xml'
    setgs['epgPath'] = 'http://127.0.0.1:12345/epg.xml'

    setgs['logoFromEpg'] = '0'
    setgs['logoPathType'] = '1'
    setgs['logoBaseUrl'] = 'http://127.0.0.1:12345/logos'
    setgs['logoPath'] = 'http://127.0.0.1:12345/logos'

    setgs['m3uCache'] = 'false'
    setgs['m3uPathType'] = '1'
    setgs['m3uUrl'] = 'http://127.0.0.1:12345/iptv.m3u'
    setgs['m3uPath'] = 'http://127.0.0.1:12345/iptv.m3u'

    setgs['startNum'] = '1'
    service_parsers.setting_writer(settings_file, setgs)

addon_id = 'plugin.video.mytv'
addon_iptvsimple_id = 'pvr.iptvsimple'
addon = xbmcaddon.Addon(id=addon_id)

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

#xbmc.executebuiltin('StopPVRManager')
addon_enabled(addon_iptvsimple_id, 'false')

myserver = http_server.MyServer(addon_path, login, password)
myserver.start()

while True:
    try:
        chans = urllib.urlopen('http://127.0.0.1:12345/iptv.m3u').read()
        log('server http started %s.' % chans)
        break
    except:
        log('waiting for server http started.')
        time.sleep(1)

iptvsimple_settings(addon_iptvsimple_path)

time.sleep(2)
#xbmc.executebuiltin('StartPVRManager')
addon_enabled(addon_iptvsimple_id, 'true')
