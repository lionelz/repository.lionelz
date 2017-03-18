import os
import addon_parsers
import sys
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


def get_logo(url):
    name = url[url.rindex('/') + 1:len(url)]
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
    xbmc.log('VOD: %s' % message, xbmc.LOGNOTICE)


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


addon_id = 'plugin.video.mytvvideo'
addon = xbmcaddon.Addon(id=addon_id)
addon_handle = int(sys.argv[1])
login, password = get_settings(addon)

channels = addon_parsers.channel_parser(login, password)

for channel in channels():
    url = channel['url']
    li = xbmcgui.ListItem(channel['name'],
        iconImage=get_logo(channel['logo']),
        thumbnailImage='')
    log('channel: %s' % (channel))
    li.setInfo('video', {
        'title': channel['program_title'],
        'plot': channel['program_description'],
        'plotoutline': channel['program_subtitle']})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
xbmcplugin.endOfDirectory(addon_handle)
