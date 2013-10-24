# -*- coding: utf-8 -*-
# This code is distributed under the two-clause BSD license.
# Copyright (c) 2013 Raphaël Barrois


"""Plugins for the djpyro server."""

from __future__ import unicode_literals

import os
import threading

from django.test import testcases


class AbstractPlugin(object):
    @classmethod
    def load(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class ServerLauncher(AbstractPlugin):
    def __init__(self, address='localhost:8081'):
        if ':' in address:
            host, port = address.rsplit(':')
        else:
            host, port = 'localhost', address

        self.host = host
        self.port = int(port)

        self._server_thread = None

    def start(self):
        self._server_thread = testcases.LiveServerThread(
            self.host, [self.port], {})
        self._server_thread.daemon = True
        self._server_thread.start()

        self._server_thread.is_ready.wait()
        if self._server_thread.error:
            # Startup failed, abort now
            raise self._server_thread.error

    def stop(self):
        self._server_thread.join()


class TestCase(AbstractPlugin):
    target_class = testcases.TestCase

    def __init__(self, **kwargs):
        super(TestCase, self).__init__(**kwargs)
        class InnerTestCase(self.target_class):
            pass

        self._inner_testcase = InnerTestCase

    def start(self):
        self._inner_testcase.setUpClass()

    def stop(self):
        self._inner_testcase.tearDownClass()


class TransactionTestCase(TestCase):
    target_class = testcases.TransactionTestCase


class LiveServerTestCase(TestCase):
    target_class = testcases.LiveServerTestCase

    def __init__(self, listen='localhost:8081', **kwargs):
        super(LiveServerTestCase, self).__init__(**kwargs)
        self._address = listen

    def start(self):
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = self._address
        super(LiveServerTestCase, self).start()


class TestEnvironment(AbstractPlugin):
    def __init__(self):
        self.runner = None
        self._runner_state = None

    def start(self):
        django_test_utils.setup_test_environment()
        self.runner = django_test_simple.DjangoTestSuiteRunner()
        self._runner_state = self.runner.setup_databases()

    def stop(self):
        self.runner.teardown_databases(self._runner_state)
        django_test_utils.teardown_test_environment()
