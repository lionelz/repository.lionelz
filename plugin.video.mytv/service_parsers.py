
import urllib
import os
import sys
import unicodedata
import zipfile
from datetime import datetime
from datetime import timedelta
from xml.dom import minidom
from xml.sax import handler
from xml.sax import make_parser


def get_datetime(date_string, format):
    try:
        datetime.strptime(date_string, format)
    except TypeError:
        datetime(*(time.strptime(date_string, format)[0:6]))


def setting_parser(file_name):
    settings = dict()
    doc = minidom.parse(file_name)
    for c1 in doc.childNodes:
        if c1.localName == 'settings':
            for c2 in c1.childNodes:
                if c2.localName == 'setting':
                    settings[c2.getAttribute('id')] = c2.getAttribute('value')
    return settings


def setting_writer(file_name, settings):
    with open(file_name, 'w') as f: 
        f.write('<settings>')
        for key, value in settings.iteritems():
            f.write('<setting id="%s" value="%s" />' % (
                key, value.encode('utf-8')))
        f.write('</settings>')


class channel_parser(object):

    _BASE_URL = 'http://www.annatel.tv/api/getchannels?login=%s&password=%s'
    _PARAMS = ''
    _ITEM = 'channel'
    _ATTRIBUTES = ['name', 'url', 'logo', 'program_title', 'program_hours',
        'program_subtitle', 'program_description']

    def __init__(self, login, password, log_path):
        self._login = login
        self._password = password
        self._log_path = log_path

    def get_channels(self):
        self._channels = list()
        self._doc = minidom.parse(
            urllib.urlopen((self._BASE_URL + self._PARAMS) % (
                urllib.quote(self._login), urllib.quote(self._password))))
        for c1 in self._doc.childNodes:
            if c1.localName == '%ss' % self._ITEM:
                for c2 in c1.childNodes:
                    if c2.localName == self._ITEM:
                        item = {}
                        for c3 in c2.childNodes:
                            if c3.localName in self._ATTRIBUTES and c3.firstChild:
                                item[c3.localName] = c3.firstChild.data
                        self._channels.append(item)
        return self._channels

    def _get_logo(self, url):
        dir_name = os.path.join(self._log_path, 'logos')
        name = url[url.rindex('/') + 1:len(url)]
        file_name = os.path.join(dir_name, name)
        if not os.path.exists(file_name):
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            with open(file_name, 'wb') as f: 
                f.write(urllib.urlopen(url).read())
        return name

    def to_m3u(self):
        self.get_channels()
        m3u = '#EXTM3U\n'
        for channel in self._channels:
            logo = self._get_logo(channel['logo'])
            m3u = (
                '{0}\n#EXTINF:-1 tvg-id="{1}" tvg-name="{1}" group-title="" '
                'tvg-logo="{2}",{3}\n{4}\n'.format(
                    m3u,
                    get_channel_id(channel['name']),
                    logo,
                    channel['name'].encode('utf-8'),
                    channel['url'].encode('utf-8')
                )
            )
        return m3u


def normalize(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def get_channel_id(name):
    for key, value in CHANNELS_LIST.iteritems():
        if isinstance(value, list):
            for val in value:
                if val == name:
                    return key
        else:
            if value == name:
                return key
    return normalize(name)


CHANNELS_LIST = {
   u'C1.telerama.fr': [u'TF1', u'TF1 HD'],
   u'C2.telerama.fr': [u'France 2', u'France 2 HD'],
   u'C3.telerama.fr': u'France 3',
   u'C4.telerama.fr': [u'Canal +', u'Canal+ HD'],
   u'C5.telerama.fr': u'France 5',
   u'C6.telerama.fr': [u'M6', u'M6 HD'],
   u'C7.telerama.fr': u'Arte',
   u'C8.telerama.fr': u'C8 (Ex D8)',
   u'C9.telerama.fr': u'W9',
   u'C10.telerama.fr': u'TMC',
   u'C11.telerama.fr': u'NT1',
   u'C12.telerama.fr': u'NRJ 12',
   u'C15.telerama.fr': u'BFM TV',
   u'C16.telerama.fr': u'i-t\xe9l\xe9',
   u'C17.telerama.fr': u'Cstar (Ex D17)',
   u'C252.telerama.fr': u'Equipe 21',
#    u'' : u'i24news',
   u'C4135.telerama.fr': u'RMC D\xe9couverte',
   u'C4139.telerama.fr': [u'BeIN Sport 1',
                          u'BeIN Sport 1 HD',
                          u'BeIN Sport 1 HD (Secours)'],
   u'C4140.telerama.fr': [u'BeIN Sport 2',
                          u'BeIN Sport 2 HD',
                          u'BeIN Sport 2 HD (Secours)'],
#    u'' : u'BeIN Sport 3 HD',
   u'C43.telerama.fr': u'Canal+ Cin\xe9ma',
   u'C47.telerama.fr': [u'Canal+ Sport', u'Canal+ Sport HD'],
   u'C4138.telerama.fr': u'Canal+ S\xe9ries',
   u'C45.telerama.fr': u'Canal+ Family',
   u'C62.telerama.fr': u'Cine+ Premier',
   u'C186.telerama.fr': u'Paris Premi\xe8re',
   u'C227.telerama.fr': u'T\xe9va',
   u'C199.telerama.fr': u'RTL9',
   u'C68.telerama.fr': u'Comedie+',
   u'C87.telerama.fr': u'EuroNews',
   u'C83.telerama.fr': u'Equidia',
   u'C124.telerama.fr': u'InfoSport',
   u'C73.telerama.fr': u'Disney Channel',
   u'C194.telerama.fr': u'Disney Junior',
   u'C75.telerama.fr': u'Disney Cinema',
   u'C171.telerama.fr': u'NickJr France',
   u'C188.telerama.fr': u'Planete+',
#    u'' : u'Arutz 1',
#    u'' : u'Arutz 2',
#    u'' : u'Arutz 10',
#    u'' : u'Annatel TV1',
#    u'' : u'Annatel TV2',
#    u'' : u'Annatel TV3',
#    u'' : u'Annatel TV4'
}


def get_epg_time(epg_time):
    split_epg = epg_time.split(' ')
    dt = get_datetime(split_epg[0], "%Y%m%d%H%M%S")
    tz = int(split_epg[1][1:3]) * 60 + int(split_epg[1][3:5])
    if (split_epg[1][0] == "+"):
        return (dt - timedelta(minutes=tz))
    else:
        return (dt + timedelta(minutes=tz))

class channel_filter(handler.ContentHandler):

    def __init__(self, out=sys.stdout):
        handler.ContentHandler.__init__(self)
        self._out = out
        self._write = True
        self._three_days = datetime.now() + timedelta(days=3)

    def startDocument(self):
        self._out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        self._out.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')

    def startElement(self, name, attrs):
        if name in ['channel', 'programme']:
            if ((attrs.get('id') in CHANNELS_LIST or 
                    attrs.get('channel') in CHANNELS_LIST) and (
                        'start' not in attrs or 
                        get_epg_time(attrs.get('start')) < self._three_days)):
                self._write = True
            else:
                self._write = False
        if self._write:
            self._out.write('<' + name)
            for (name, value) in attrs.items():
                self._out.write(' %s="%s"' % (name, value.encode('utf-8')))
            self._out.write('>')

    def endElement(self, name):
        if self._write:
            self._out.write('</%s>' % name)
        if name in ['channel', 'programme']:
            self._write = True

    def characters(self, content):
        if self._write:
            self._out.write(content.encode('utf-8'))

    def ignorableWhitespace(self, content):
        if self._write:
            self._out.write(content)
        
    def processingInstruction(self, target, data):
        if self._write:
            self._out.write('<?%s %s?>' % (target, data))


class programs_parser(object):

    def __init__(self, url, tmp_dir):
        self._url = url
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        self._tmp_dir = tmp_dir
        self._xml_file = None

    def _getzip_and_unzip(self):
        zip_filename = os.path.join(
            self._tmp_dir, self._url[self._url.rindex('/') + 1:len(self._url)])
        cur_date = datetime.now()
        ts_file = os.path.join(self._tmp_dir, 'ts')
        download_zip = True
        if not os.path.exists(ts_file):
            download_zip = True
        else:
            with open(ts_file, 'r') as f:
                ld = f.read()
                last_download = get_datetime(ld, '%Y-%m-%d %H:%M:%S.%f')
            if cur_date - timedelta(days=3) > last_download:
                download_zip = True
        if download_zip:
            with open(ts_file, 'w') as f: 
                f.write(cur_date.strftime('%Y-%m-%d %H:%M:%S.%f'))
            with open(zip_filename, 'wb') as f: 
                f.write(urllib.urlopen(self._url).read())
 
        if zipfile.is_zipfile(zip_filename):
            with zipfile.ZipFile(zip_filename, 'r') as z:
                z.extract(z.namelist()[0], self._tmp_dir)
                self._xml_file = os.path.join(self._tmp_dir, z.namelist()[0])


    def parse(self, dest_file_name):
        self._getzip_and_unzip()
        parser = make_parser()
        with open(dest_file_name, 'w') as f:
            parser.setContentHandler(channel_filter(out=f))
            parser.parse(self._xml_file)
