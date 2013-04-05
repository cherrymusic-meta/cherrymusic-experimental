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

from collections import namedtuple


import cherrymusicserver as main
import cherrymusicserver.db.persist as db

from cherrymusicserver import session

DBNAME = 'users'
DBVERSION = '1'


@db.persistant
class User(namedtuple('UserTuple', 'userid name admin password salt')):
    def __new__(cls, userid, name, admin=0, password='', salt=''):
        return super(cls, cls).__new__(cls, userid, name, admin, password, salt)

TYPE = User


main.db.require(DBNAME, DBVERSION)


@cherrypy.tools.json_out()
def GET(name=None, **kwargs):
    print('fetch', name, kwargs)
    if name is None:
        whereop = ', '.join(k + '=?' for k in kwargs)
        wherevalues = tuple(kwargs.values())
        where = (whereop, wherevalues) if whereop else ()
        result = db.fetch(DBNAME, TYPE, where)
        return list(result)
    obj = db.fetchone(DBNAME, TYPE, {'name': name})
    if obj is None:
        raise cherrypy.HTTPError(404)
    return obj


@cherrypy.tools.json_in()
def PUT(name):
    try:
        obj = TYPE(**cherrypy.request.json)
    except TypeError as e:
        raise cherrypy.HTTPError(400, str(e))
    existing = GET(name)
    if existing is None:
        raise cherrypy.HTTPError(404)
    session.authorize(require_id=existing.userid, admin_override=True)
    assert existing.userid == obj.userid
    dic = existing._asdict()
    dic.update(obj._asdict())
    obj = TYPE(**dic)
    db.update(DBNAME, TYPE, obj)
    print('updated', existing, obj)


@cherrypy.tools.json_in()
def POST():
    session.authorize(require_admin=True)
    try:
        obj = TYPE(userid=None, **cherrypy.request.json)
    except TypeError as e:
        raise cherrypy.HTTPError(400, str(e))
    newobj = db.persist(DBNAME, TYPE, obj)
    cherrypy.response.status = 201
    print('added', newobj)


def DELETE(name):
    existing = GET(name)
    if existing.userid <= 1:
        raise cherrypy.HTTPError(403, 'Forbidden')
    session.authorize(require_id=existing.userid, admin_override=True)
    db.delete(DBNAME, TYPE, existing)
    print('deleted', name)


# @main.service.provider('users')
# class Resource(main.http.Resource):
#     def __init__(self):
#         main.db.require(DBNAME, DBVERSION)

#     @cherrypy.tools.json_out()
#     def GET(self, name=None, **kwargs):
#         print('fetch', name, kwargs)
#         if name is None:
#             return list(db.fetch(DBNAME, TYPE, **kwargs))
#         obj = db.fetchone(DBNAME, TYPE, {'name': name})
#         if obj is None:
#             raise cherrypy.HTTPError(404)
#         return obj

#     @cherrypy.tools.json_in()
#     def PUT(self, name):
#         try:
#             obj = TYPE(**cherrypy.request.json)
#         except TypeError as e:
#             raise cherrypy.HTTPError(400, e)
#         existing = self.GET(name)
#         if existing is None:
#             raise cherrypy.HTTPError(404)
#         assert existing.userid == obj.userid
#         dic = existing._asdict()
#         dic.update(obj._asdict())
#         obj = TYPE(**dic)
#         db.update(DBNAME, TYPE, obj)
#         print('updated', existing, obj)

#     @cherrypy.tools.json_in()
#     def POST(self):
#         try:
#             obj = TYPE(userid=None, **cherrypy.request.json)
#         except TypeError as e:
#             raise cherrypy.HTTPError(400, str(e))
#         newobj = db.persist(DBNAME, TYPE, obj)
#         cherrypy.response.status = 201
#         print('added', newobj)

#     def DELETE(self, name):
#         if 'system' == name:
#             raise cherrypy.HTTPError(403, 'Forbidden')
#         existing = self.GET(name)
#         db.delete(DBNAME, TYPE, existing)
#         print('deleted', name)
