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
import time

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

DBNAME = media.DBNAME
QUEUESIZE = 5000


def convert(olddbpath):
    db.resetdb(media.DBNAME)
    db.ensure_requirements(media.DBNAME)
    _add_tagtypes()
    _add_tracks(olddbpath)
    _add_tags()


def _add_tagtypes():
    types = (
        ('filesystem', 'Files'),
        ('artist', 'Artists'),
        ('album', 'Albums'),
        ('title', 'Titles'),
    )
    for t in types:
        db.persist.persist(DBNAME, media._TagType, media._TagType(None, *t))


def _add_tracks(olddbpath):
    log.info('adding tracks...')
    connector = db.sql.SQLiteConnector().bound(olddbpath)
    count = 0
    starttime = last = now = time.time()
    for dirname, subdirs, subfiles in walk_old_db(connector):
        now = time.time()
        if now - last > 1:
            last = now
            rate = count / (now - starttime)
            log.info('%r (%d, %d/s)', dirname[:60], count, rate)
        for filename in subfiles:
            _add_file_as_track(dirname, filename)
        count += len(subfiles)
    dbqueue.finalize()
    log.info('done.')


def _add_tags():
    log.info('adding tags...')
    count = 0
    starttime = last = now = time.time()
    tracks = db.persist.fetch(DBNAME, media.Track)
    for track in tracks:
        now = time.time()
        if 1 < now - last:
            last = now
            rate = count / (now - starttime)
            log.info('%r (%d, %d/s)', track.content[:60], count, rate)
        _add_path_taggings(track.trackid, track.content)
        _add_meta_taggings(track.trackid, track.content)
        count += 1
    dbqueue.finalize()


def _add_file_as_track(basepath, name):
    relpath = os.path.join(basepath, name)
    dbqueue.persist(media.Track(None, relpath))
    # for name in relpath.split(os.path.sep):


def _add_path_taggings(trackid, filepath):
    pathnames = os.path.splitext(filepath)[0].split(os.path.sep)
    for i in range(len(pathnames)):
        _add_tag('filesystem', 'Files', pathnames[i], trackid, i)


def _add_meta_taggings(trackid, filepath):
    pathnames = os.path.splitext(filepath)[0].split(os.path.sep)
    if len(pathnames) > 1 and not pathnames[0].startswith('+'):
        _add_tag('artist', 'Artist', pathnames[0], trackid)
    if len(pathnames) > 2:
        _add_tag('album', 'Albums', pathnames[1], trackid)
    _add_tag('title', 'Titles', os.path.splitext(pathnames[-1])[0], trackid)


def _add_tag(type, grp, text, trackid, seq=None):
    userid = 0
    public = 1
    tag = media.Tag(None, None, text, type, grp, userid, public, seq, trackid)
    dbqueue.persist(tag)
    return tag


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


class QueuedPersist(object):
    def __init__(self, dbname, maxsize):
        self.dbname = dbname
        self.maxsize = maxsize
        self.queues = {}

    def getqueue(self, cls):
        try:
            return self.queues[cls]
        except KeyError:
            return self.queues.setdefault(cls, Queue(self.maxsize))

    def persist(self, obj):
        cls = obj.__class__
        q = self.getqueue(cls)
        q.put(obj)
        if q.full():
            db.persist.persist_many(self.dbname, cls, q.queue)
            q.queue.clear()

    def finalize(self):
        for cls in self.queues:
            q = self.getqueue(cls)
            if not q.empty():
                db.persist.persist_many(self.dbname, cls, q.queue)
                q.queue.clear()
        self.queues.clear()

dbqueue = QueuedPersist(DBNAME, QUEUESIZE)


if __name__ == '__main__':
    convert(sys.argv[1])
