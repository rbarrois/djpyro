# -*- coding: utf-8 -*-
# This code is published under the BSD license

"""DjPyro server."""

from __future__ import unicode_literals

import Pyro4
from Pyro4.utils import flame

class Server(object):
    def __init__(self, port=0, host=None, unixsocket=None, **kwargs):
        super(Server, self).__init__(**kwargs)
        self._host = host
        self._port = port
        self._unixsocket = unixsocket
        self._daemon = None
        self._closed = False

    def run(self, plugins=None):
        Pyro4.config.SERIALIZERS_ACCEPTED = set(['pickle'])
        Pyro4.config.FLAME_ENABLED = True

        self._daemon = Pyro4.Daemon(
            host=self._host,
            port=self._port,
            unixsocket=self._unixsocket,
        )

        if plugins is None:
            plugins = {}

        for plugin_name, plugin in plugins.items():
            self._daemon.register(plugin, 'plugin-%s' % plugin_name)
        self._daemon.register(self, 'server')
        flame.start(self._daemon)
        self._daemon.requestLoop()

    def kill(self):
        self._daemon.shutdown()
