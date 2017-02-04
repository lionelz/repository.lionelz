import os
import addon_parsers
import sys
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


def get_logo(name):
    name = name.replace(
        'canalplus', 'canalp').replace(
            'disneycinema', 'disney-cinema-beta').replace(
                'nrj12', 'nrj12_300x300')
    url = 'http://client.annatel.tv/channels/%s.png' % name
    dir_name =  os.path.join(
        xbmc.translatePath('special://masterprofile').decode('utf-8'),
        'addon_data',
        addon_id,
        'logos',
    )
    file_name = os.path.join(dir_name, '%s.png' % name)
    if not os.path.exists(file_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        with open(file_name, 'wb') as f: 
            f.write(urllib.urlopen(url).read())
    return file_name

def build_url(query):
    url = sys.argv[0] + '?' + urllib.urlencode(query)
    log(url)
    return url


def log(message):
    xbmc.log('VOD: %s' % message, xbmc.LOGDEBUG)


def get_settings(addon):
    login = addon.getSetting('login')
    password = addon.getSetting('password')
    log('login: %s, password: %s' % (login, password))
    while (login.strip() == '' or password.strip() == ''):
        xbmc.executebuiltin('XBMC.Notification("32000","32001", 10000)')                
        result = addon.openSettings()
        login = addon.getSetting('login')
        password = addon.getSetting('password')
        log('login: %s, password: %s' % (login, password))
    return login, password


addon_id = 'plugin.video.myvod'
addon = xbmcaddon.Addon(id=addon_id)
args = urlparse.parse_qs(sys.argv[2][1:])
addon_handle = int(sys.argv[1])
login, password = get_settings(addon)

channels = addon_parsers.channel_parser(login, password)
dates = addon_parsers.date_parser(login, password)
programs = addon_parsers.program_parser(login, password)

mode = args.get('mode', None)
stream = args.get('stream', None)
day = args.get('day', None)

log('addon_handle: %d, mode: %s, stream: %s, day: %s' % (
    addon_handle, mode, stream, day))

if mode is None:
    for channel in channels():
        url = build_url({
            'mode': 'day',
            'stream': channel['stream'],
        })
        li = xbmcgui.ListItem(
            channel['name'],
            iconImage=get_logo(channel['stream']),
            thumbnailImage='')
        li.setInfo('video', {'title': channel['name']})
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'day':
    for date in dates(stream[0]):
        url = build_url({
            'mode': 'program',
            'stream': stream[0],
            'day': date['day']
        })
        li = xbmcgui.ListItem(
            date['display'],
            iconImage=get_logo(stream[0]),
            thumbnailImage='')
        li.setInfo('video', {'title': date['display']})
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'program':
    for program in programs(stream[0], day[0]):
        url = program['url']
        li = xbmcgui.ListItem(program['name'],
            iconImage=get_logo(stream[0]),
            thumbnailImage='')
        li.setInfo('video', {
            'title': program['name'], 'plot': program['description']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
