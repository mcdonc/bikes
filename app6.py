from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.security import Allow, remember, forget
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPFound
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='blogentry_show')
    def show(self):
        return Response('Shown')

    @view_config(route_name='blogentry_delete', permission='delete')
    def delete(self):
        return Response('Deleted')

    @view_config(route_name='login')
    def login(self):
        userid = self.request.matchdict['userid']
        headers = remember(self.request, userid)
        return HTTPFound('/blog/1', headers=headers)

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound('/blog/1', headers=headers)

class RootFactory(object):
    # [1]
    def __init__(self, request):
        self.__acl__ = [(Allow, 'fred', 'delete')]

if __name__ == '__main__':
    authn_policy = AuthTktAuthenticationPolicy('soseekrit')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
        )
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.add_route('login', 'login/{userid}')
    config.add_route('logout', 'logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# Not the same anymore.  Only 'fred' can delete blog entries.
#
# New features:
#
# [1] We changed our ACL to allow only the principal id 'fred' to delete
#     blog entries.  No longer an any authenticated principal delete
#     blog entries.
#
# Noteworthy:
#
# - "Principal" means "userid" or "groupid".  It's just a string, typically
#   (although it can be any basic Python type).
