DjPyro
======


This library integrates `Pyro <http://pypi.python.org/pypi/pyro4>` with Django.

It provides a new command, ``django-admin.py runpyro``, that will start a
Pyro server and might also start a Django runserver.

It also provides extensions to the Pyro "flame" protocol,
notably a ``kill()`` command that will terminate the remote server.

Purpose
-------

The goal of DjPyro is to ease integration testing including Django projects.

Simply do:

.. code-block:: sh

    django-admin.py runpyro 1000 --with-http=8000 &
    django-admin.py runpyro 1001 --with-http=8001 &

    python
    >>> import djpyro
    >>> s1 = djpyro.Client('localhost:1000')
    >>> s2 = djpyro.Client('localhost:1001')
    >>> run_tests()
    >>> s1.kill()
    >>> s2.kill()
    >>> exit()
