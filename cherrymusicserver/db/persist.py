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
from cherrymusicserver import db

_persist_info = {}


def fetch(dbname, cls, paramdict=None, groups='', order='', limit=None, offset=None):
    connector = db.connect.BoundConnector(dbname)
    stmt = _persist_info[cls]['select']
    values = ()
    if paramdict:
        stmt += ' WHERE ' + ' AND '.join(k + '=?' for k in paramdict)
        values += tuple(paramdict.values())
    if groups:
        # stmt += ' ' + 'GROUP BY {0}'.format(', '.join(groups))
        stmt += ' ' + 'GROUP BY {0}'.format(groups)
    if order:
        stmt += ' ' + 'ORDER BY {0}'.format(groups)
    if limit is not None:
        stmt += ' LIMIT {0}'.format(limit)
    if offset is not None:
        stmt += ' OFFSET {0}'.format(offset)
    cursor = connector.execute(stmt, values)
    return (cls(*r) for r in cursor.fetchall())


def query(dbname, query, params=()):
    connector = db.connect.BoundConnector(dbname)
    cursor = connector.execute(query, params)
    return (r for r in cursor.fetchall())


def fetchone(dbname, cls, paramdict={}):
    result = list(fetch(dbname, cls, paramdict, limit=1))
    if result:
        return result[0]
    return None


def persist(dbname, cls, obj):
    assert isinstance(obj, cls)
    stmt = _persist_info[cls]['insert']
    values = tuple(obj)[1:]
    cursor = _transact(dbname, stmt, values)
    return cls(cursor.lastrowid, *values)


def persist_many(dbname, cls, objs):
    stmt = _persist_info[cls]['insert']
    params = tuple(o[1:] for o in objs)
    connector = db.connect.BoundConnector(dbname)
    with connector.transaction() as txn:
        txn.executemany(stmt, params)


def update(dbname, cls, obj):
    assert isinstance(obj, cls)
    stmt = _persist_info[cls]['update']
    values = tuple(obj)[1:] + tuple(obj)[:1]
    _transact(dbname, stmt, values)


def delete(dbname, cls, obj):
    assert isinstance(obj, cls)
    stmt = _persist_info[cls]['delete']
    values = (obj[0],)
    _transact(dbname, stmt, values)


def _transact(dbname, stmt, params):
    connector = db.connect.BoundConnector(dbname)
    with connector.transaction() as txn:
        cursor = txn.execute(stmt, params)
    return cursor


def _execute(dbname, stmt, params):
    cnx = db.connect.BoundConnector(dbname).connection()
    cursor = cnx.execute(stmt, params)
    return cursor


def persistant(cls):
    table = cls.__name__.lower() + 's'
    columns = cls._fields
    select = 'SELECT {0} FROM {1}'.format(', '.join(columns), table)
    insert = 'INSERT INTO {table}({columns}) VALUES ({placeholders})'.format(
        table=table,
        columns=', '.join(columns[1:]),
        placeholders=', '.join('?' for _ in columns[1:])
    )
    update = 'UPDATE {table} SET {setters} WHERE {id} = ?'.format(
        table=table,
        setters=', '.join('%s=?' % c for c in columns[1:]),
        id=columns[0]
    )
    delete = 'DELETE FROM {table} WHERE {id} = ?'.format(
        table=table, id=columns[0])
    _persist_info[cls] = {
        'table': table,
        'columns': columns,
        'select': select,
        'insert': insert,
        'update': update,
        'delete': delete,
    }
    return cls
