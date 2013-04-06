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
import os
import sys

import logging as log
log.basicConfig(level=log.INFO, format='%(levelname)-8s | %(message)s')

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


import cherrymusicserver as main
main.init_services()

from cherrymusicserver import db
from cherrymusicserver import media

from cherrymusicserver.resources import files


def convert(olddbpath):
    db.resetdb(media.DBNAME)
    db.ensure_requirements(media.DBNAME)
    connector = db.sql.SQLiteConnector().bound(olddbpath)
    for dirname, subdirs, subfiles in walk_old_db(connector):
        if 0 == dirname.count(os.path.sep):
            log.info('%r (%d)', dirname, len(subfiles))
        for filename in subfiles:
            _add_file(dirname, filename)
    # with _addqueue.mutex:
    if not _addqueue.empty():
        db.persist.persist_many(media.DBNAME, media.Tag, _addqueue.queue)
        _addqueue.queue.clear()


def _add_file(basepath, name):
    relpath = os.path.join(basepath, name)
    track = media.addTrack(relpath)
    _add_path_tags(track.trackid, relpath)
    _add_meta_tags(track.trackid, relpath)


def _add_path_tags(trackid, filepath):
    pathnames = os.path.splitext(filepath)[0].split(os.path.sep)
    for i in range(len(pathnames)):
        _add_tag('filesystem', 'Files', pathnames[i], trackid, i)


def _add_meta_tags(trackid, filepath):
    pathnames = os.path.splitext(filepath)[0].split(os.path.sep)
    if len(pathnames) > 1 and not pathnames[0].startswith('+'):
        _add_tag('artist', 'Artist', pathnames[0], trackid)
    if len(pathnames) > 2:
        _add_tag('album', 'Albums', pathnames[1], trackid)
    _add_tag('title', 'Titles', os.path.splitext(pathnames[-1])[0], trackid)


_addqueue = Queue(maxsize=500)


def _add_tag(type, grp, text, trackid, seq=None):
    userid = 0
    public = 1
    tag = media.Tag(None, None, text, type, grp, userid, public, seq, trackid)
    _addqueue.put(tag)
    # with _addqueue.mutex:
    if _addqueue.full():
        db.persist.persist_many(media.DBNAME, media.Tag, _addqueue.queue)
        _addqueue.queue.clear()


def walk_old_db(connector):
    with connector.connection() as conn:
        cursor = conn.cursor()
        cursor.row_factory = lambda crs, row: files.File(*row)
        get_dirs = """SELECT rowid, filename, filetype, isdir, parent
                      FROM files
                      WHERE isdir = 1
                      ORDER BY parent;"""
        get_files = """SELECT rowid, filename, filetype, isdir, parent
                        FROM files
                        WHERE parent = ? AND isdir = 0;"""
        get_subdirs = """SELECT rowid, filename, filetype, isdir, parent
                          FROM files
                          WHERE parent = ? AND isdir = 1;"""
        dircache = {-1: ''}
        rows = cursor.execute(get_dirs).fetchall()
        rows = [files.File(-1, '', '', 1, -1)] + rows
        for row in rows:
            dirname = row.name + row.ext
            dirname = os.path.join(dircache[row.parent], dirname)
            dircache[row.id] = dirname
            subdir_rows = cursor.execute(get_subdirs, (row.id,)).fetchall()
            file_rows = cursor.execute(get_files, (row.id,)).fetchall()
            subdirs = [r.name + r.ext for r in subdir_rows]
            subfiles = [r.name + r.ext for r in file_rows]
            yield dirname, subdirs, subfiles
        cursor.close()
    conn.close()

if __name__ == '__main__':
    convert(sys.argv[1])
