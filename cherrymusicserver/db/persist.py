import cherrymusicserver.db as db

_persist_info = {}


def special_fetch(dbname, cls, where=(), groups='', limit=None, offset=None):
    connector = db.connect.BoundConnector(dbname)
    stmt = _persist_info[cls]['select']
    values = ()
    if where:
        stmt += ' WHERE ' + where[0]
        values += where[1]
    if groups:
        # stmt += ' ' + 'GROUP BY {0}'.format(', '.join(groups))
        stmt += ' ' + 'GROUP BY {0}'.format(groups)
    if limit is not None:
        stmt += ' LIMIT {0}'.format(limit)
    if offset is not None:
        stmt += ' OFFSET {0}'.format(offset)
    cursor = connector.execute(stmt, values)
    return (cls(*r) for r in cursor.fetchall())


def fetch(dbname, cls, paramdict=None, groups='', limit=None, offset=None):
    connector = db.connect.BoundConnector(dbname)
    stmt = _persist_info[cls]['select']
    values = ()
    if paramdict:
        stmt += ' WHERE ' + ' AND '.join(k + '=?' for k in paramdict)
        values += tuple(paramdict.values())
    if groups:
        # stmt += ' ' + 'GROUP BY {0}'.format(', '.join(groups))
        stmt += ' ' + 'GROUP BY {0}'.format(groups)
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
