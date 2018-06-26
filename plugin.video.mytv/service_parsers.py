
import urllib
import urllib2
import os
import sys
import time
import unicodedata
import zipfile
from datetime import datetime
from datetime import timedelta
from xml.dom import minidom
from xml.sax import handler, make_parser, saxutils
import _strptime


def get_datetime(date_string, format):
    try:
        return datetime.strptime(date_string, format)
    except TypeError:
        return datetime(*(time.strptime(date_string, format)[0:6]))


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
    with open(file_name, 'w+') as f: 
        f.write('<settings>')
        f.write(os.linesep)
        for key, value in settings.iteritems():
            f.write('   <setting id="%s" value="%s" />' % (
                key, value.encode('utf-8')))
            f.write(os.linesep)
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
   u'C192.api.telerama.fr': [u'TF1', u'TF1 HD'],
   u'C4.api.telerama.fr': [u'France 2', u'France 2 HD'],
   u'C80.api.telerama.fr': u'France 3',
   u'C34.api.telerama.fr': [u'Canal +', u'Canal+ HD'],
   u'C47.api.telerama.fr': u'France 5',
   u'C118.api.telerama.fr': [u'M6', u'M6 HD'],
   u'C111.api.telerama.fr': u'Arte',
   u'C445.api.telerama.fr': u'C8',
   u'C119.api.telerama.fr': u'W9',
   u'C195.api.telerama.fr': u'TMC',
   u'C446.api.telerama.fr': [u'NT1', u'TFX'],
   u'C444.api.telerama.fr': u'NRJ 12',
#   u'':u'Annatel+',
   u'C481.api.telerama.fr': u'BFM TV',
   u'C226.api.telerama.fr': u'CNews',
   u'C458.api.telerama.fr': u'CStar',
#   u'': u'Equipe 21',
#    u'' : u'i24news',
   u'C1400.api.telerama.fr': u'RMC D\xe9couverte',
#   u'': [u'BeIN Sport 1',
#         u'BeIN Sport 1 HD',
#         u'BeIN Sport 1 HD (Secours)'],
#   u'': [u'BeIN Sport 2',
#         u'BeIN Sport 2 HD',
#         u'BeIN Sport 2 HD (Secours)'],
#   u'': u'BeIN Sport 3 HD',
#   u'': u'SFR Sport 1',
#   u'': u'SFR Sport 2',
#   u'': u'SFR Sport 3',
#   u'': u'Canal+ Cin\xe9ma',
#   u'': [u'Canal+ Sport', u'Canal+ Sport HD'],
#   u'': u'Canal+ S\xe9ries',
#   u'': u'Canal+ Family',
#   u'': u'Cine+ Premier',
#   u'': u'Cine+ Frisson',
#   u'': u'Cine+ Famiz',
   u'C145.api.telerama.fr': u'Paris Premi\xe8re',
#   u'': u'T\xe9va',
#   u'': u'RTL9',
#   u'': u'Comedie+',
#   u'': u'EuroNews',
#   u'': u'Equidia',
#   u'': u'InfoSport',
#   u'': u'Disney Channel',
#   u'': u'Disney Junior',
#   u'': u'Disney Cinema',
#   u'': u'NickJr France',
#   u'': u'Planete+',
#   u'': u'Israel Torah',
#   u'' : u'Arutz 1',
#   u'' : u'Arutz 10',
#   u'' : u'Arutz 12 (Keshet)',
#   u'' : u'Arutz 13 (Reshet)',
#   u'' : u'Arutz 20',
#   u'' : u'Annatel TV1',
#   u'' : u'Annatel TV2',
#   u'' : u'Annatel TV3',
#   u'' : u'Canal Decale'
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
        self._delta = datetime.now() + timedelta(days=2)

    def startDocument(self):
        self._out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        self._out.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')

    def startElement(self, name, attrs):
        if name in ['channel', 'programme']:
            if ((attrs.get('id') in CHANNELS_LIST or 
                    attrs.get('channel') in CHANNELS_LIST) and (
                        'start' not in attrs or 
                        get_epg_time(attrs.get('start')) < self._delta)):
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
            self._out.write(saxutils.escape(content.encode('utf-8')))

    def ignorableWhitespace(self, content):
        if self._write:
            self._out.write(content)
        
    def processingInstruction(self, target, data):
        if self._write:
            self._out.write('<?%s %s?>' % (target, data))


def check_ts(ts_name, t_delta):
    old = True
    cur_date = datetime.now()
    if os.path.exists(ts_name):
        with open(ts_name, 'r') as f:
            ld = f.read()
            last_download = get_datetime(ld, '%Y-%m-%d %H:%M:%S.%f')
        old = cur_date - t_delta > last_download
    if old:
        with open(ts_name, 'w') as f:
            f.write(cur_date.strftime('%Y-%m-%d %H:%M:%S.%f'))
    return old


class programs_parser(object):

    def __init__(self, url, tmp_dir):
        self._url = url
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        self._tmp_dir = tmp_dir
        self._out = None
        self._zip_filename = os.path.join(
            self._tmp_dir, self._url[self._url.rindex('/') + 1:len(self._url)])

    def _getzip(self):
        cur_date = datetime.now()
        ts_file = os.path.join(self._tmp_dir, 'ts_zip')
        is_old = check_ts(ts_file, timedelta(days=6))
        if is_old:
            with open(self._zip_filename, 'wb') as f: 
                z = urllib2.urlopen(self._url)
                while True:
                    chunk = z.read(80)
                    if not chunk:
                        break
                    f.write(chunk)

    def parse_to_out(self, out):
        self._getzip()
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces,False)
        parser.setFeature(handler.feature_validation,False)
        parser.setFeature(handler.feature_external_ges, False)
        parser.setContentHandler(channel_filter(out=out))
        with zipfile.ZipFile(self._zip_filename, 'r') as z:
            with z.open(z.namelist()[0]) as fi:
                parser.parse(fi)

    def parse(self, dest_file_name):
        self._getzip()
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces,False)
        parser.setFeature(handler.feature_validation,False)
        parser.setFeature(handler.feature_external_ges, False)
        with open(dest_file_name, 'w') as f:
            parser.setContentHandler(channel_filter(out=f))
            with zipfile.ZipFile(self._zip_filename, 'r') as z:
                with z.open(z.namelist()[0]) as fi:
                    parser.parse(fi)
