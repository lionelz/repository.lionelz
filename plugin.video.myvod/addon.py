import os
import addon_parsers
import sys
import urllib
import xbmcaddon
import xbmcgui
import xbmcplugin


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def get_settings(addon):
    login = addon.getSetting('login')
    password = addon.getSetting('password')
    while (not login or login.strip() == '' or
           not password or password.strip() == ''):
        result = addon.openSettings()
        if result:
            login = addon.getSetting('login')
            password = addon.getSetting('password')
        else:
            xbmc.executebuiltin('XBMC.Notification("32000","32001", 15000)')                
    return login, password


addon = xbmcaddon.Addon(id='plugin.video.myvod')
base_url = sys.argv[0]
args = urlparse.parse_qs(sys.argv[2][1:])
addon_handle = int(sys.argv[1])
login, password = get_settings(addon)

channels = addon_parsers.channel_parser(login, password)
dates = addon_parsers.date_parser(login, password)
programs = addon_parsers.program_parser(login, password)

xbmcplugin.setContent(addon_handle, 'movies')

mode = args.get('mode', None)
stream = args.get('stream', None)
day = args.get('day', None)
if mode is None:
    for channel in channels():
        url = build_url({
            'mode': 'day',
            'stream': channel['stream']
        })
        li = xbmcgui.ListItem(channel['name'], iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'day':
    for date in dates(stream[0]):
        url = build_url({
            'mode': 'program',
            'stream': stream[0],
            'day': date['day']
        })
        li = xbmcgui.ListItem(date['display'], iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'program':
    (mode[1], mode[2])
    for program in programs(stream[0], day[0]):
        url = program['url']
        li = xbmcgui.ListItem(date['name'], iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
