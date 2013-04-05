import cherrypy

class Resource(object):

    exposed = True

    def GET(self):
        raise cherrypy.HTTPError(405, 'Method Not Allowed')

    def PUT(self):
        raise cherrypy.HTTPError(405, 'Method Not Allowed')

    def POST(self):
        raise cherrypy.HTTPError(405, 'Method Not Allowed')

    def DELETE(self):
        raise cherrypy.HTTPError(405, 'Method Not Allowed')
