import os
import service_parsers
import shutil
import sys
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

    
def iptvsimple_settings(iptvsimple_addon, addon_iptvsimple_path):
    settings_file = os.path.join(addon_iptvsimple_path, 'settings.xml')
    if (not os.path.isfile(settings_file)):
        iptvsimple_addon.setSetting('epgPathType', '0')
    setgs = service_parsers.setting_parser(settings_file)

    setgs['epgPathType'] = '0'
    setgs['epgPath'] = os.path.join(addon_iptvsimple_path, 'epg.xml')
    setgs['logoPathType'] = '0'
    setgs['logoPath'] = os.path.join(addon_iptvsimple_path, 'logos')
    setgs['m3uPathType'] = '0'
    setgs['m3uPath'] = os.path.join(addon_iptvsimple_path, 'iptv.m3u')

    service_parsers.setting_writer(settings_file, setgs)

addon_id = 'plugin.video.mytv'
addon_iptvsimple_id = 'pvr.iptvsimple'
addon = xbmcaddon.Addon(id=addon_id)
iptvsimple_addon = xbmcaddon.Addon(id=addon_iptvsimple_id)

xbmc.executebuiltin('StopPVRManager')
login, password = get_settings(addon)

addon_iptvsimple_path = os.path.join(
    xbmc.translatePath('special://masterprofile').decode('utf-8'),
    'addon_data',
    addon_iptvsimple_id,
)

log(addon_iptvsimple_path)

iptvsimple_settings(iptvsimple_addon, addon_iptvsimple_path)

shutil.copyfile(
    os.path.join(
        xbmc.translatePath('special://home').decode('utf-8'),
        'addons',
        addon_id,
        'xmltv.dtd'
    ),
    os.path.join(addon_iptvsimple_path, 'xmltv.dtd')
)

# Get channels
channels = service_parsers.channel_parser(
    login, password, addon_iptvsimple_path)
with open(os.path.join(addon_iptvsimple_path, 'iptv.m3u'), 'w') as f: 
    f.write(channels.to_m3u())

# Get epg
p_parser = service_parsers.programs_parser(
    'http://xmltv.dtdns.net/download/complet.zip',
    addon_iptvsimple_path)
p_parser.parse(os.path.join(addon_iptvsimple_path, 'epg.xml')) 

xbmc.executebuiltin('StartPVRManager')
