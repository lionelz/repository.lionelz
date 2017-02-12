import BaseHTTPServer
import service_parsers
import time
import threading
import os


class MyTVHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_GET(s):
    if s.path.startswith('/logos'):
        s.send_response(200)
        s.send_header('Content-type', 'image/png')
        s.end_headers()
        logo =  s.path[s.path.rindex('/') + 1:len(s.path)]
        with open(os.path.join(
            MyTVHandler.myServer.work_dir, 'logos', logo), 'rb') as f: 
            s.wfile.write(f.read())
    if s.path == '/epg.xml':
        s.send_response(200)
        s.send_header('Content-type', 'application/xml')
        s.end_headers()
        p_parser = service_parsers.programs_parser(
            'http://xmltv.dtdns.net/download/complet.zip',
            MyTVHandler.myServer.work_dir
        )
        p_parser.parse_to_out(s.wfile) 
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


class MyServer(threading.Thread):

    def __init__(self, work_dir,
                 login, password, host_name='localhost', port=12345):
        super(MyServer, self).__init__()
        self.work_dir = work_dir
        self.login = login
        self.password = password
        self.host_name = host_name
        self.port = port
        MyTVHandler.myServer = self

    def run(self):
        httpd = BaseHTTPServer.HTTPServer(
            (self.host_name, self.port), MyTVHandler)
        try:
            httpd.serve_forever()
        except:
            pass
        httpd.server_close()
