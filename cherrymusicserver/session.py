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
