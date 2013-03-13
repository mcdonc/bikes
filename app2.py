from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='blogentry_show')
    def show(self):
        return Response('Shown')

    # [1]
    @view_config(route_name='blogentry_delete')
    def delete(self):
        userid = self.request.cookies.get('userid')
        if userid is None:
            raise HTTPForbidden()
        return Response('Deleted')

    # [2]
    @view_config(route_name='login')
    def login(self):
        userid = self.request.matchdict['userid']
        headers = [('Set-Cookie', 'userid=%s' % userid)]
        return HTTPFound('/blog/1', headers=headers)

    # [3]
    @view_config(route_name='logout')
    def logout(self):
        headers = [
            ('Set-Cookie',
             'userid=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT')
            ]
        return HTTPFound('/blog/1', headers=headers)

# [4]
if __name__ == '__main__':
    config = Configurator()
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.add_route('login', 'login')
    config.add_route('logout', 'logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# Basic security; only authenticated users can delete blog entries.  all others
# can view blog entries.
#
# New features:
#
# [1] Imperative authorization code to check whether a logged in user can delete
# [2] Login view to service authorization checks.  Just a stub, a real app 
#     would require password checking.
# [3] Logout view to forget login credentials.
# [4] Wiring up login and logout views into config.
#
# Noteworthy:
#
# - No frameworky bits, it's all your code.  Party like it's 1999.
#
# - Imperative code to check whether a logged in user can delete must
#   be repeated everywhere to be useful.
#
# - Married to cookie-based authentication throughout codebase (everywhere:
#   [1], [2], and [3]).  A change to the authentication mechanism implies
#   visiting each place the imperative security checking is done.
#
# - Authentication is "who you are".  Authorization is "what you can do".  In
#   this application, authentication and authorization are intertwined.
#   However, logically, while authorization typically depends on
#   authentication, authentication is independent of authorization.  Our
#   application does not take this into consideration, however; it has no
#   abstractions that would allow it to.

