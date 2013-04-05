import cherrypy
exposed = True

from cherrymusicserver import media


@cherrypy.tools.json_out()
def GET(**kwargs):
    return media.search(**kwargs)
