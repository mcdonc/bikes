#!/usr/bin/env python
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.security import Authenticated, remember, forget
from pyramid.authentication import AuthTktAuthenticationPolicy
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='blogentry_show')
    def show(self):
        return Response('Shown')

    @view_config(route_name='blogentry_delete',
                 permission='delete')
    def delete(self):
        return Response('Deleted')

    # [5]
    @view_config(route_name='login')
    def login(self):
        userid = self.request.params.get('userid')
        headers = remember(self.request, userid)
        return Response(
            'Logged in as %s' % userid,
            headers=headers
            )

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return Response(
            'Logged out',
            headers=headers
            )

class DumbAuthorizationPolicy(object):
    def permits(self, context, principals,
                permission):
        return Authenticated in principals

# [1]
if __name__ == '__main__':
    authn_policy = AuthTktAuthenticationPolicy(
        'soseekrit')
    authz_policy = DumbAuthorizationPolicy()
    config = Configurator(
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
        )
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# Exactly the same as app3.py except we ditch our authorization policy for
# one provided by Pyramid.
#
# New features:
#
# [1] We use AuthTktAuthenticationPolicy instead of our homebrewed
#     DumbAuthenticationPolicy.
#
# Noteworthy:
#
# - AuthTktAuthenticationPolicy used in [1] is offered by Pyramid.  It
#   implements the authentication policy API just like our homebrewed one
#   did, except it uses an Apache ``mod_auth_tkt`` "authentication ticket"
#   stored in a cookie.  Nominally it's more secure as a result, but the real
#   win lies more in needing to maintain less security code.  It's typically a 
#   good idea to use a built-in authentication policy unless you need the
#   control.
#
# - Pyramid has several built in authentication policies:  
#   AuthTktAuthenticationPolicy, SessionAuthenticationPolicy, 
#   BasicAuthenticationPolicy, RemoteUserAuthenticationPolicy.
#
# - If your clients don't authenticate in a single way, you can combine
#   existing authentication policies using the ``pyramid_multiauth`` package.
#   For example, web service clients need basic authentication but
#   other clients need cookie-based auth.
#
# - We continue to use our DumbAuthorizationPolicy unchanged.
#   Authentication and authorization policies are independent.  If written
#   correctly, an authentication policy can be swapped for another 
#   implementation as necessary without needing to change the application's
#   authorization policy.  Likewise, an authorization policy can be
#   swapped for another without needing to change the authentication policy.


