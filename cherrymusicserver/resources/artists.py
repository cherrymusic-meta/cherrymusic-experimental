import cherrypy
exposed = True

import cherrymusicserver as main
from cherrymusicserver import media


@cherrypy.tools.json_out()
def GET(artist=None, **kwargs):
    grp = media.Group('type', 'artist')
    if not artist:
        stmt = '''SELECT "text", COUNT(1) AS "size"
                  FROM tags
                  WHERE (userid = 0 OR public = 1) AND type='artist'
                  GROUP BY text;'''
        results = media.query(stmt)
        return list(grp._subgroup('text', r[0], r[1]) for r in results)
    stmt = '''SELECT album.text, COUNT(1)
              FROM
                (SELECT * FROM tags WHERE (userid = 0 OR public = 1) AND type='artist' AND text=?) as artist
              JOIN
                (SELECT * FROM tags WHERE type='album') as album
              USING (trackid)
              GROUP BY album.text'''
    params = (artist,)
    results = media.query(stmt, params)
    return list()
