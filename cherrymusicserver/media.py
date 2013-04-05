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
import functools

from collections import namedtuple

import cherrymusicserver as main
from cherrymusicserver import session
from cherrymusicserver.db import persist as db


_TagType = db.persistant(namedtuple('_TagType', 'typeid type groupname'))
_Text = db.persistant(namedtuple('_Text', 'textid textdata'))
_Tag = db.persistant(namedtuple('_Tag', 'tagid typeid textid userid public'))
_Tagged = db.persistant(namedtuple('_Tagged', 'tgid tagid trackid seq'))

Tag = db.persistant(
    namedtuple('Tag', 'id tagid text type groupname userid public seq trackid'))
Track = db.persistant(namedtuple('Track', 'trackid content'))


DBNAME = 'media'
DBVERSION = '1'
TYPE = Tag

main.db.require(DBNAME, DBVERSION)

# dbdef = main.db.defs.get(DBNAME)
# with main.db.connect.BoundConnector(DBNAME).transaction() as txn:
#     txn.executescript(dbdef[DBVERSION]['testdata.sql'])

fetch = functools.partial(db.fetch, DBNAME)
fetchone = functools.partial(db.fetchone, DBNAME)
special_fetch = functools.partial(db.special_fetch, DBNAME)
persist = functools.partial(db.persist, DBNAME)
update = functools.partial(db.update, DBNAME)
delete = functools.partial(db.delete, DBNAME)
query = functools.partial(db.query, DBNAME)


def addTag(text, type, groupname, userid, public, seq, trackid):
    main.session.authorize(require_id=userid)
    tag = Tag(None, None, text, type, groupname, userid, public, seq, trackid)
    return persist(Tag, tag)


def addTrack(content):
    return persist(Track, Track(None, content))


# class Group(namedtuple('GroupTuple', 'name type size query constraints url')):

#     _types = ('type', 'text', 'userid', 'seq', 'search')

#     def __new__(cls, name, type, size=None, query='', constraints={}, url=''):
#         return super(Group, cls).__new__(cls, name, type, size, query, constraints, url)

#     def _subgroup(self, name, type, size=None, constraints={}):
#         c = dict(self.constraints)
#         c.update({type: name})
#         c.update(constraints)
#         return self._replace(name=name, type=type, size=size, constraints=c)

#     @property
#     def _select(self):
#         constraints = ' AND '.join(self._where)
#         stmt = ("""SELECT trackid FROM tags {where}""").format(
#             where='WHERE ' + constraints if constraints else '')
#         return stmt

#     @property
#     def _where(self):
#         where = ('text LIKE ?',) if self.query else ()
#         where += tuple(k + '=?' for k in self.constraints)
#         return where

#     @property
#     def _params(self):
#         params = ('%' + self.query + '%') if self.query else ()
#         params += tuple(self.constraints.values())
#         return params


from collections import defaultdict


class Group(namedtuple('GroupTuple', 'type name size constraints')):
    def __new__(cls, type, name, size=None, constraints=None):
        if constraints is None:
            constraints = defaultdict(tuple)
        constraints[type] += (name,)
        return super(Group, cls).__new__(cls, type, name, size, constraints)

    @property
    def _filters(self):
        for field, values in self.constraints.items():
            if not values:
                continue
            if 1 == len(values):
                yield filter(field, values[0])
            else:
                yield in_(field, values)

    def _add_constraints(self, field, *values):
        c = defaultdict(tuple, self.constraints)
        c[field] += tuple(values)
        return self._replace(constraints=c)

    def _subgroup(self, type, name, size=None):
        # c = defaultdict(tuple, self.constraints)
        # c[self.type] += (self.name,)
        return Group(type, name, size, self.constraints)


class SearchGroup(Group):

    def __new__(cls):
        constraints = defaultdict(tuple)
        return super(Group, cls).__new__(cls, None, None, None, constraints)

    # def _subgroup(self, name, type, size=None):
    #     return self._replace(name=name, type=type, size=size)


class InfixOp(namedtuple('InfixOpTuple', 'left op right')):
    def __str__(self):
        return '{0} {1} {2}'.format(*self)

    @property
    def _sql(self):
        return '{0} {1} {2}'.format(self.left._sql, self.op, self.right._sql)

    @property
    def _params(self):
        return self.left._params + self.right._params


def or_(left, right):
    return InfixOp(left, 'OR', right)


class filter(InfixOp):
    def __new__(cls, fieldname, value, op='='):
        return super(filter, cls).__new__(cls, fieldname, op, value)

    @property
    def _sql(self):
        return '{0} {1} ?'.format(self.left, self.op)

    @property
    def _params(self):
        return (self.right,)


class in_(filter):
    def __new__(cls, fieldname, values):
        return super(cls, cls).__new__(cls, fieldname, tuple(values), op='IN')

    @property
    def _sql(self):
        return '{field} IN ({placeholders})'.format(
            field=self.left,
            placeholders=', '.join('?' for _ in self.right))

    @property
    def _params(self):
        return self.right


class Tracks(object):

    def __init__(self, user):
        self.user = user
        self.core = or_(filter('userid', user.userid), filter('public', 1))
        self.posfilters = ()

    def with_filters(self, *filters):
        other = Tracks(self.user)
        other.posfilters += tuple(filters)
        return other

    def with_tagids(self, *tagids):
        filters = (filter('tagid', tagid) for tagid in tagids)
        return self.with_filters(*filters)

    def with_userid(self, userid):
        return self.with_filters(filter('userid', userid))

    def with_types(self, *types):
        filters = (filter('type', t) for t in types)
        return self.with_filters(*filters)

    @property
    def _sql(self):
        select = 'SELECT trackid FROM tags WHERE '
        core = select + self.core._sql
        posfilters = (' INTERSECT ' + select + f._sql for f in self.posfilters)
        return core + ''.join(posfilters)

    @property
    def _params(self):
        params = self.core._params
        for f in self.posfilters:
            params += f._params
        return params


def search(query=None):
    grp = SearchGroup()
    if query:
        tagids = db.query(DBNAME, 'SELECT tagid FROM _tags WHERE textid IN (SELECT textid FROM texts WHERE textdata LIKE ?)', ('%' + query + '%',))
        grp = grp._add_constraints('tagid', *tagids)
    return expand(grp)


grouptype_following = {
    'search': 'type',
    'type': 'text',
    'text': 'text',
}


def expand(grp):
    if grp.size is not None and grp.size < 4:
        return grp
    return expand_by(grouptype_following[grp.type], grp)


def expand_by(type, group):
    user = session.authorize()
    tracks = Tracks(user).with_filters(*group._filters)
    stmt = 'SELECT {type}, COUNT(1) as size FROM ({sub}) GROUP BY {type}'.format(
        type=type,
        sub=tracks._sql)
    print(stmt, tracks._params)
    results = query(stmt, tracks._params)
    return list(group._subgroup(name=r[0], type=type, size=r[1]) for r in results)
