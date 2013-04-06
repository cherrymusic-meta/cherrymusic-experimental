#!/usr/bin/python3
#
# CherryMusic - a standalone music server
# Copyright (c) 2012 Tom Wallroth & Tilman Boerner
#
# Project page:
#   http://fomori.org/cherrymusic/
# Sources on github:
#   http://github.com/devsnd/cherrymusic/
#
# CherryMusic is based on
#   jPlayer (GPL/MIT license) http://www.jplayer.org/
#   CherryPy (BSD license) http://www.cherrypy.org/
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

#python 2.6+ backward compability
from __future__ import unicode_literals

import cherrypy
import logging
import os

config = {
    'server.port': 8080,
    'media.basedir': '/home/til/Music',
    'server.localhost_only': True,
    'runtime.path.data': 'data',
    'runtime.path.res': 'res',
    'runtime.path.plugins': 'plugins',
}

from cherrymusicserver import db
from cherrymusicserver import http
from cherrymusicserver import patch
from cherrymusicserver import resources
from cherrymusicserver import service
from cherrymusicserver import session

VERSION = "0.24.1"
DESCRIPTION = "an mp3 server for your browser"
LONG_DESCRIPTION = """CherryMusic is a music streaming
    server written in python. It's based on cherrypy and jPlayer.
    You can search your collection, create and share playlists with
    other users. It's able to play music on almost all devices since
    it happends in your browser and uses HTML5 for audio playback.
    """


def init_services():
    # service.provide(db.sql.TmpConnector)
    service.provide(db.sql.SQLiteConnector, kwargs={'datadir': config['runtime.path.data']})


class CherryMusic:

    def __init__(self):
        init_services()
        db.ensure_requirements()
        self.start()

    def start(self):
        socket_host = "127.0.0.1" if config['server.localhost_only'] else "0.0.0.0"

        resourcedir = os.path.abspath(config['runtime.path.res'])

        cherrypy.config.update({
            'server.socket_port': config['server.port'],
        })

        cherrypy.config.update({
            'log.error_file': 'server.log',
            'environment': 'production',
            'server.socket_host': socket_host,
            'server.thread_pool': 30,
            'tools.sessions.on': True,
            'tools.sessions.timeout': 60 * 24,
        })

        cherrypy.tree.mount(
            _Root(), '/',
            config={
                '/': {
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                },
                '/res': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': resourcedir,
                    'tools.staticdir.index': 'index.html',
                    'tools.caching.on': False,
                },
                '/serve': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': config['media.basedir'],
                    'tools.staticdir.index': 'index.html',
                    'tools.encode.on': True,
                    'tools.encode.encoding': 'utf-8',
                    'tools.caching.on': False,
                },
                '/favicon.ico': {
                    'tools.staticfile.on': True,
                    'tools.staticfile.filename': resourcedir+'/favicon.ico',
                },
            })
        logging.info('Starting server on port %s ...' % config['server.port'])

        cherrypy.lib.caching.expires(0)  # disable expiry caching
        cherrypy.engine.start()
        cherrypy.engine.block()

    def serverless(self):
        cherrypy.server.unsubscribe()
        self.start()

    def server(self):
        cherrypy.config.update({'log.screen': True})
        self.start()


class _Root(http.Resource):

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            print('looking up', name)
            return resources.get(name)
        except LookupError:
            print('not found')
            raise AttributeError(name)

    def GET(self):
        return """
<HTML>
<HEAD></HEAD
<BODY>
    Hello there!
</BODY>
</HTML>
"""
