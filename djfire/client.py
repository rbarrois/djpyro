# -*- coding: utf-8 -*-
# This code is published under the BSD license

"""DjPyro client."""

from __future__ import unicode_literals


import Pyro4
from Pyro4.utils import flame


class PluginProxy(object):
    def __init__(self, remote_location):
        self.remote_location = remote_location

    def __getitem__(self, key):
        return Pyro4.Proxy('PYRO:plugin-%s@%s' % (key, self.remote_location))


class Client(object):
    def __init__(self, remote_location, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.remote_location = remote_location
        self._flame_client = None
        self._server_proxy = None
        self.plugins = PluginProxy(self.remote_location)

    def connect(self):
        Pyro4.config.SERIALIZER = 'pickle'
        self._flame_client = flame.connect(self.remote_location)
        self._server_proxy = Pyro4.Proxy('PYRO:server@%s' % self.remote_location)

    def kill(self):
        # Don't wait for the result, since we'll kill the server.
        self._server_proxy._pyroOneway.add('kill')
        self._server_proxy.kill()
        self._server_proxy._pyroRelease()

    # Flame wrapper
    def module(self, name):
        return self._flame_client.module(name)

    def console(self):
        return self._flame_client.console()
