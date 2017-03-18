
import urllib
from xml.dom import minidom

class channel_parser(object):

    _BASE_URL = 'http://www.annatel.tv/api/getchannels?login=%s&password=%s'
    _PARAMS = ''
    _ITEM = 'channel'
    _ATTRIBUTES = ['name',
                   'url',
                   'logo',
                   'program_title',
                   'program_hours',
                   'program_subtitle',
                   'program_description']

    def __init__(self,  login, password):
        self._login = login
        self._password = password

    def __call__(self,  *args, **kwargs):
        t = (urllib.quote(self._login), urllib.quote(self._password))
        for arg in args:
            t = t + (urllib.quote(arg), )
        self._doc = minidom.parse(
            urllib.urlopen((self._BASE_URL + self._PARAMS) % t))
        res = list()
        for c1 in self._doc.childNodes:
            if c1.localName == '%ss' % self._ITEM:
                for c2 in c1.childNodes:
                    if c2.localName == self._ITEM:
                        item = {}
                        for att in self._ATTRIBUTES:
                            item[att] = ''
                        for c3 in c2.childNodes:
                            if c3.localName in self._ATTRIBUTES:
                                if c3.firstChild:
                                    item[c3.localName] = c3.firstChild.data
                        res.append(item)
        return res
