import cherrypy
exposed = True

import cherrymusicserver as main

def POST(*args, **kwargs):
    print(args, kwargs)
    user = main.session.login(kwargs['username'], kwargs['password'])
    print('logged in: ', user)
