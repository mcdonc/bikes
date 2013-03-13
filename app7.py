from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.security import Allow, Authenticated, remember, forget
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

# [1]
class Resource(object):
    def __init__(self, name='', acl=None, parent=None):
        self.children = {}
        self.__name__ = name
        self.__parent__ = parent
        if acl is not None:
            self.__acl__ = acl

    def add_subresource(self, name, acl=None):
        self.children[name] = Resource(name, acl=acl, parent=self)

    def __getitem__(self, name):
        return self.children[name]

    def __repr__(self):
        return '<Resource named %r at %s>' % (self.__name__, id(self))

# [2]
def root_factory(request):
    root = Resource('', acl=[(Allow, 'fred', 'delete')])
    root.add_subresource('1', acl=[(Allow, Authenticated, 'delete')])
    return root

if __name__ == '__main__':
    authn_policy = AuthTktAuthenticationPolicy('soseekrit')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
        root_factory=root_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
        )
    config.add_route('blogentry_show', '/blog/{id}')
    # [3]
    config.add_route('blogentry_delete', '/blog/{id}/delete', traverse='/{id}')
    config.add_route('login', 'login/{userid}')
    config.add_route('logout', 'logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# New outcome: Fred can delete all blog entries.  Additionally, any
# authenticated user can delete blog entry named '1'.
#
# - FYI, circref formed but not cleaned up.
