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

import os
from collections import namedtuple

import cherrymusicserver as main

from cherrymusicserver import media
from cherrymusicserver import metainfo
from cherrymusicserver.db import persist as db

_cp_config = {
    'tools.staticdir.on': True,
    'tools.staticdir.dir': main.config['media.basedir'],
    'tools.staticdir.index': 'index.html',
    'tools.encode.on': True,
    'tools.encode.encoding': 'utf-8',
    'tools.caching.on': False,
}

File = db.persistant(namedtuple('File', 'id name ext isdir parent'))

DBNAME = 'files'
DBVERSION = '1'
TYPE = File

main.db.require(DBNAME, DBVERSION)


def PUT(update):
    if update == 'update':
        _update()


def _update():
    main.db.resetdb(DBNAME)
    main.db.ensure_requirements(DBNAME)
    _add_dir(main.config['media.basedir'], '', parentid=-1)


def _add_dir(basepath, name, parentid):
    f = db.persist(DBNAME, File, File(None, name, '', 1, parentid))
    fullpath = os.path.join(basepath, name)
    for childname in os.listdir(fullpath):
        if os.path.isdir(os.path.join(fullpath, childname)):
            _add_dir(fullpath, childname, f.id)
        else:
            _add_file(fullpath, childname, f.id)


def _add_file(basepath, name, parentid):
    f = File(None, name, os.path.splitext(name)[1], 0, parentid)
    f = db.persist(DBNAME, File, f)
    fullpath = os.path.join(basepath, name)
    relpath = fullpath[len(main.config['media.basedir']) + 1:]
    track = media.addTrack(relpath)
    _add_path_tags(track.trackid, relpath.split(os.path.sep))
    _add_meta_tags(track.trackid, fullpath)


def _add_path_tags(trackid, pathnames):
    for i in range(len(pathnames)):
        media.addTag(
            pathnames[i], 'filesystem', 'Files', 0, 1, i, trackid)


def _add_meta_tags(trackid, fullpath):
    info = metainfo.getSongInfo(fullpath)
    if info.artist != '-':
        media.addTag(
            info.artist, 'artist', 'Artists', 0, 1, None, trackid)
    if info.title != '-':
        media.addTag(
            info.title, 'title', 'Titles', 0, 1, None, trackid)
    if info.album != '-':
        media.addTag(
            info.album, 'album', 'Albums', 0, 1, info.track, trackid)
