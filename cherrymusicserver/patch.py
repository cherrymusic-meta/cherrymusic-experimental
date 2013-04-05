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
import cherrypy
import codecs
import sys
import threading

cherrypyReqVersion = '3'
cherrypyCurrVersion = str(cherrypy.__version__)
if cherrypyCurrVersion < cherrypyReqVersion:
    print("""
cherrypy version is too old!
Current version: %s
Required version: %s or higher
""" % (cherrypyCurrVersion, cherrypyReqVersion))
    sys.exit(1)

# woraround for cherrypy 3.2.2:
# https://bitbucket.org/cherrypy/cherrypy/issue/1163/attributeerror-in-cherrypyprocessplugins
if sys.version_info >= (3, 3):
    threading._Timer = threading.Timer


"""patch cherrypy crashing on startup because of double checking
for loopback interface, see:
https://bitbucket.org/cherrypy/cherrypy/issue/1100/cherrypy-322-gives-engine-error-when
"""


def fake_wait_for_occupied_port(host, port):
    return
cherrypy.process.servers.wait_for_occupied_port = fake_wait_for_occupied_port
"""end of port patch"""

"""workaround for cherrypy not using unicode strings for URI, see:
https://bitbucket.org/cherrypy/cherrypy/issue/1148/wrong-encoding-for-urls-containing-utf-8
"""
cherrypy.lib.static.__serve_file = cherrypy.lib.static.serve_file


def serve_file_utf8_fix(path, content_type=None, disposition=None, name=None, debug=False):
    path = codecs.decode(codecs.encode(path, 'latin-1'), 'utf-8')
    return cherrypy.lib.static.__serve_file(path, content_type, disposition, name, debug)


cherrypy.lib.static.serve_file = serve_file_utf8_fix
"""end of unicode workaround"""
