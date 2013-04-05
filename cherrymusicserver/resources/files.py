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

File = db.persistant(namedtuple('File', 'fileid name ext isdir parent'))

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
            _add_dir(fullpath, childname, f.fileid)
        else:
            _add_file(fullpath, childname, f.fileid)


def _add_file(basepath, name, parentid):
    f = File(None, name, os.path.splitext(name)[1], 0, parentid)
    f = db.persist(DBNAME, File, f)
    fullpath = os.path.join(basepath, name)
    relpath = fullpath[len(main.config['media.basedir']) + 1:]
    track = media.addTrack(relpath)
    _add_path_tags(track.trackid, os.path.split(relpath))
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
