import BaseHTTPServer
import service_parsers
import time
import threading
import os

from datetime import timedelta


class MyTVHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_GET(s):
    if s.path.startswith('/logos'):
        s.send_response(200)
        s.send_header('Content-type', 'image/png')
        s.end_headers()
        logo = s.path[s.path.rindex('/') + 1:len(s.path)]
        with open(os.path.join(
            MyTVHandler.myServer.work_dir, 'logos', logo), 'rb') as f: 
            s.wfile.write(f.read())
    if s.path == '/epg.xml':
        s.send_response(200)
        s.send_header('Content-type', 'application/xml')
        s.end_headers()
        file_name = os.path.join(
            MyTVHandler.myServer.work_dir, 'epg.xml')
        epg_updater = UpdateEpg(MyTVHandler.myServer.work_dir, file_name)
        ts_file = os.path.join(
            MyTVHandler.myServer.work_dir, 'ts_epg')
        try:
            MyTVHandler.myServer.lock.acquire()
            is_old = service_parsers.check_ts(ts_file, timedelta(hours=4))
            if not os.path.exists(file_name) or is_old:
                epg_updater.run()
            with open(file_name, 'r') as f: 
                s.wfile.write(f.read())
        finally:
            MyTVHandler.myServer.lock.release()
        return
    if s.path == '/iptv.m3u':
        s.send_response(200)
        s.send_header('Content-type', 'application/x-mpegURL')
        s.end_headers()
        channels = service_parsers.channel_parser(
            MyTVHandler.myServer.login,
            MyTVHandler.myServer.password,
            MyTVHandler.myServer.work_dir
        )
        s.wfile.write(channels.to_m3u())
        return


class UpdateEpg(threading.Thread):

    def __init__(self, work_dir, file_name):
        super(UpdateEpg, self).__init__()
        self._work_dir = work_dir
        self._tmp_file_name = '%s.tmp' % file_name.encode('utf-8')
        self._file_name = file_name

    def run(self):
        p_parser = service_parsers.programs_parser(
            'https://github.com/lionelz/repository.lionelz/raw/master/lionelz.zip',
            self._work_dir
        )
        p_parser.parse(self._tmp_file_name)
        if os.path.exists(self._file_name):
            os.remove(self._file_name)
        os.rename(self._tmp_file_name, self._file_name)


class MyServer(threading.Thread):

    def __init__(self, work_dir,
                 login, password, host_name='0.0.0.0', port=12345):
        super(MyServer, self).__init__()
        self.work_dir = work_dir
        self.login = login
        self.password = password
        self.host_name = host_name
        self.port = port
        self.lock = threading.Lock()
        MyTVHandler.myServer = self

    def run(self):
        httpd = BaseHTTPServer.HTTPServer(
            (self.host_name, self.port), MyTVHandler)
        try:
            httpd.serve_forever()
        except:
            pass
        httpd.server_close()
