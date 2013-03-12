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
        headers = remember(self.request, 'fred')
        return HTTPFound('/blog/1', headers=headers)

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound('/blog/1', headers=headers)

# [2]
class RootFactory(object):
    def __init__(self, request):
        self.__acl__ = [(Allow, Authenticated, 'delete')]

if __name__ == '__main__':
    authn_policy = AuthTktAuthenticationPolicy('soseekrit')
    authz_policy = ACLAuthorizationPolicy()
    # [1]
    config = Configurator(
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
        )
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.add_route('login', 'login')
    config.add_route('logout', 'logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# Exactly the same as app2.py, app3.py, and app4.py. Basic security; only
# authenticated users can delete blog entries.  all others can view blog 
# entries.
#
# New features:
#
# [1] We use Pyramid's ACLAuthorizationPolicy instead of our homebrewed
#     DumbAuthorizationPolicy.  We now pass a "root factory" into our 
#     configurator. Our ACLAuthorizationPolicy will use instances
#     of objects produced by this root factory to determine whether or
#     not someone is permitted to execute a view.
#
# [2] We supply a "RootFactory" class.  Instances of this class possess an
#     ACL (as ``__acl__``).  ACL stands for "Access Control List".
#
# Noteworthy:
#
# - This is typically where people go off the rails.  We've added yet another
#   layer of abstraction by using the ACLAuthorizationPolicy.  This abstraction
#   requires us to understand this "root factory" thing.
#
# - The benefit: we no longer own any imperative code which does 
#   authorization or authentication.  It's all declarative.


