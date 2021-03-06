# -*- coding: utf-8 -*-
"""
HTTP test server for writing tests against an "external" server.
"""

import atexit
import socket
import threading
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


class HTTPServerIPV6(HTTPServer):
    address_family = socket.AF_INET6


class HTTPStaticTestServer(object):
    """
    Static test server that server files from the local directory and
    sub-directories. Highly recommended that each test suite puts the files it
    wants served into a custom sub-directory under 'data/'. Then tests can
    reach the files by using the url:
    http://localhost:8088/data/<custom-sub-directory>/<file>

    This server is run in a thread over the local loopback and should be
    started and stopped on each test or test suite run.

    It's recommended that start be put in setUpClass and stop be put in
    tearDownClass to avoid the overhead of starting and stopping on each test
    run.
    """

    def __init__(self, port=8088):
        self.server = HTTPServerIPV6(('', port), SimpleHTTPRequestHandler)
        self.server.timeout = 0.1  # timeout after a tenth of a second
        self._is_running = False
        self._server_thread = None
        _SERVERS.append(self)

    def _serve(self):
        while self._is_running:
            self.server.handle_request()

    def start(self):
        self._is_running = True
        self._server_thread = threading.Thread(target=self._serve)
        self._server_thread.setDaemon(True)
        self._server_thread.start()

    def stop(self):
        self._is_running = False
        self._server_thread.join()
        self._server_thread = None
        _SERVERS.remove(self)


_SERVERS = []


def _cleanup_servers():
    """
    Cleanup all of the running server in case we were ctrl+c'd
    """
    for server in _SERVERS:
        server.stop()


atexit.register(_cleanup_servers)
