import cherrypy
exposed = True

import functools

from collections import namedtuple

import cherrymusicserver as main

import cherrymusicserver.session as session
from cherrymusicserver.db import persist as db

_TagType = db.persistant(namedtuple('_TagType', 'typeid type groupname'))
_Text = db.persistant(namedtuple('_Text', 'textid textdata'))
_Tag = db.persistant(namedtuple('_Tag', 'tagid typeid textid userid public'))
_Tagged = db.persistant(namedtuple('_Tagged', 'tgid tagid trackid seq'))

Tag = db.persistant(
    namedtuple('Tag', 'id text type groupname userid public seq trackid'))

DBNAME = 'media'
DBVERSION = '1'
TYPE = Tag

main.db.require(DBNAME, DBVERSION)

# dbdef = main.db.defs.get(DBNAME)
# with main.db.connect.BoundConnector(DBNAME).transaction() as txn:
#     txn.executescript(dbdef[DBVERSION]['testdata.sql'])

fetch = functools.partial(db.fetch, DBNAME)
fetchone = functools.partial(db.fetchone, DBNAME)
persist = functools.partial(db.persist, DBNAME)
update = functools.partial(db.update, DBNAME)
delete = functools.partial(db.delete, DBNAME)


@cherrypy.tools.json_out()
def GET(**params):
    user = session.authorize()
    # params = (('userid='), (user.userid,))
    params.update({'userid': user.userid})
    print('fetch', user.name, params)
    return list(db.fetch(DBNAME, TYPE, params))
