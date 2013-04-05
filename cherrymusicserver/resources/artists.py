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
exposed = True

import cherrymusicserver as main
from cherrymusicserver import media


@cherrypy.tools.json_out()
def GET(artist=None, **kwargs):
    grp = media.Group('type', 'artist')
    if not artist:
        stmt = '''SELECT "text", COUNT(1) AS "size"
                  FROM tags
                  WHERE (userid = 0 OR public = 1) AND type='artist'
                  GROUP BY text;'''
        results = media.query(stmt)
        return list(grp._subgroup('text', r[0], r[1]) for r in results)
    stmt = '''SELECT album.text, COUNT(1)
              FROM
                (SELECT * FROM tags WHERE (userid = 0 OR public = 1) AND type='artist' AND text=?) as artist
              JOIN
                (SELECT * FROM tags WHERE type='album') as album
              USING (trackid)
              GROUP BY album.text'''
    params = (artist,)
    results = media.query(stmt, params)
    return list()
