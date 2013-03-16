#!/usr/bin/env python
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from waitress import serve

class DemoViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='set')
    def set(self):
        return Response(
            'OK',
            headerlist=[('Set-Cookie', 'foo=1')]
            )

    @view_config(route_name='show')
    def show(self):
        return Response(
            self.request.cookies['foo']
            )


if __name__ == '__main__':
    config = Configurator()
    config.add_route('set', '/set')
    config.add_route('show', '/show')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
