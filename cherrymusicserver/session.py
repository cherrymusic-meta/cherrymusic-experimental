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

from collections import namedtuple

from cherrymusicserver.db import persist as db


@db.persistant
class User(namedtuple('UserTuple', 'userid name admin password salt')):
    def __new__(cls, userid, name, admin=0, password='', salt=''):
        return super(cls, cls).__new__(cls, userid, name, admin, password, salt)


def login(username, password):
    user = _system_user()
    _session()['user'] = user
    return user


def logout():
    cherrypy.lib.sessions.expire()


def authorize(require_id=None, require_admin=False, admin_override=False):
    try:
        user = _session().get('user', None)
    except:
        user = None
    if user is None:
        user = login(None, None)
    if require_id is not None and require_id != user.userid:
        if not (admin_override and user.admin):
            raise cherrypy.HTTPError(401)
    if require_admin and not user.admin:
        raise cherrypy.HTTPError(401)
    return user


def _system_user():
    return db.fetchone('users', User, {'userid': 0})


def _session():
    return getattr(cherrypy, 'session', {})
