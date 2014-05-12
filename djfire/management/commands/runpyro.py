# -*- coding: utf-8 -*-
# This code is distributed under the two-clause BSD license.
# Copyright (c) 2013 Raphaël Barrois

import optparse
import os

from django.core.management.base import BaseCommand
from django.utils import importlib

from ... import server as djfire_server
from ... import plugins as djfire_plugins

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option('--http-server', action='store',
            default='', help="Run a HTTP server at the given host:port"),
        optparse.make_option('--test-db', action='store_true',
            default=False, help="Run within Django's test environment"),
        optparse.make_option('--listen', action='store', default='localhost:51000',
            help="Listen for Pyro requests on the given address/socket"),
    )

    help = (
        "Run a Pyro4 server in the context of the Django project. "
        "Plugins will be available as 'plugin-name' in the client.")
    args = "[name:plugin ...]"

    def handle(self, *plugin_specs, **options):
        test_db = options['test_db']
        http_server = options['http_server']
        listen = options['listen']

        plugins = self._load_plugins(plugin_specs)

        stack = []
        if test_db:
            stack.append(djfire_plugins.TestEnvironment())

        if http_server:
            stack.append(djfire_plugins.ServerLauncer(http_server))

        self.launch(listen, stack=stack, plugins=plugins)

    def launch(self, listen, plugins, stack=()):
        if listen.startswith('/') or listen.startswith('.'):
            server_kwargs = {'unixsocket': os.path.abspath(listen)}
        else:
            # IPv6
            host, port = listen.rsplit(':', 1)
            server_kwargs = {'host': host, 'port': int(port)}

        server = djfire_server.Server(**server_kwargs)

        for pre in stack:
            self.stdout.write("Starting %r" % pre)
            pre.start()

        self.stdout.write("Starting server on %s..." % listen)
        if plugins:
            self.stdout.write("Exposing plugins [%s]" %
                    ', '.join('%s:%r' % item for item in plugins.items()))
        server.run(plugins)
        self.stdout.write("Server done, exiting...")

        for post in reversed(stack):
            self.stdout.write("Stopping %r" % post)
            post.stop()

    def _load_plugins(self, plugin_specs):
        plugins = {}
        for spec in plugin_specs:
            if ':' not in spec:
                raise ValueError("Invalid spec %s (doesn't look like name:path)" % spec)
            name, path = spec.split(':', 1)
            if '.' not in path:
                path = 'djfire.plugins.%s' % path
            modname, plugin_name = path.rsplit('.', 1)
            mod = importlib.import_module(modname)
            plugin = getattr(mod, plugin_name)

            plugins[name] = plugin

        return plugins
