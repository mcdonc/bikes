from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    # [1]
    @view_config(route_name='blogentry_show')
    def show(self):
        return Response('Shown')

    # [1]
    @view_config(route_name='blogentry_delete')
    def delete(self):
        return Response('Deleted')


if __name__ == '__main__':
    config = Configurator()
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# No security; users can both show and delete any blog entry.
#
# Features:
#
# [1] Show and delete views stubbed out for purposes of brevity.
#
# Noteworthy:
#
# - When you visit /blog/id it will invoke the "show" view.
#
# - When you visit /blog/id/delete it will invoke the "delete" view.
