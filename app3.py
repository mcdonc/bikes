from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.security import remember, forget, Authenticated, Everyone
from pyramid.httpexceptions import HTTPFound
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='blogentry_show')
    def show(self):
        return Response('Shown')

    # [4]
    @view_config(route_name='blogentry_delete', permission='delete')
    def delete(self):
        return Response('Deleted')

    # [5]
    @view_config(route_name='login')
    def login(self):
        headers = remember(self.request, 'fred')
        return HTTPFound('/blog/1', headers=headers)

    # [6]
    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound('/blog/1', headers=headers)

# [1]
class DumbAuthenticationPolicy(object):
    def unauthenticated_userid(self, request):
        userid = request.cookies.get('userid')
        return userid

    authenticated_userid = unauthenticated_userid

    def effective_principals(self, request):
        principals = [Everyone]
        userid = self.unauthenticated_userid(request)
        if userid is not None:
            principals.append(Authenticated)
            principals.append(userid)
        return principals

    def remember(self, request, principal, **kw):
        return [('Set-Cookie', 'userid=fred')]

    def forget(self, request):
        return [
            ('Set-Cookie',
             'userid=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT')
            ]

# [2]        
class DumbAuthorizationPolicy(object):
    def permits(self, context, principals, permission):
        if permission == 'delete':
            return Authenticated in principals
        return False

# [3]
if __name__ == '__main__':
    authn_policy = DumbAuthenticationPolicy()
    authz_policy = DumbAuthorizationPolicy()
    config = Configurator(
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
    
# Same thing as app1.py.  Basic security; only authenticated users can delete 
# blog entries and all others can view blog entries.
#
# New features: 
#
# [1] A user-defined Pyramid authentication policy.  It implements the notional
#     Pyramid authentication policy API.
# [2] A user-defined Pyramid authorization policy.  It implements the notional
#     Pyramid authorization policy API.
# [3] We wire the authentication and authorization policies into config via
#     the Configurator.
# [4] A "permission" argument to the ``view_config`` of blogentry_delete
#     replaces imperative authorization code that used to live in method body.
# [5] We use ``pyramid.security.remember`` instead of setting a cookie by
#     hand in the login view.
# [6] We use ``pyramid.security.forget`` instead of removing a cookie by hand
#     in the logout view.
#
# Noteworthy:
#
# - The new authentication policy [1] uses the same cookie-based authentication 
#   scheme that we used in app2.py.  We've just moved the code.  In the login 
#   view [5], we set the cookie via ``remember``, which calls our 
#   authentication policy's ``remember`` method.  Our ``logout`` method in
#   [6] causes our authentication policy's ``forget`` method to be called, which
#   expires the cookie.
#
# - The ``permission`` attached to our ``delete`` method [4] will be the 
#   ``permission`` value passed to  the ``permits`` method of our authorization
#   policy [2] before Pyramid attempts to execute the ``blogentry_delete`` view. 
#   ``permission='delete'`` means "allow execution of this view if the user 
#   who causes its invocation is permitted to delete"; it's the authorization 
#   policy's job to answer this question.
#
# - Our new authorization policy [2] performs very basic security checking using 
#   the principals output by our authentication policy [1].  The return value of
#   ``effective_principals`` of our authentication policy [1] is the 
#   ``principals`` value passed to the ``permits`` method of our authorization 
#   policy [2].
#
# - Our new authorization policy [2] ``permits`` method checks if the principal 
#   named ``Authenticated`` is in the ``principals`` passed and allows
#   the action if the permission under consideration is ``delete``.
#
# - Authentication policy completely divorced from application code.  Changing
#   to, e.g. session-based authentication or Basic HTTP Authentication would
#   require changing the authentication_policy argument in [3] to use a
#   different implementation, but app code would be otherwise unchanged.
#
# - Pyramid is now made responsible for allowing or permitting the execution
#   of the ``delete`` view [4] instead of us.  Authorization is normalized via
#   the ``permission`` attached to the view via the ``view_config`` decorator.
#
# - If our authorization policy's ``permits`` method returns False, Pyramid 
#   returns a 403 Forbidden error by default (configurable via a "forbidden 
#   view").
#
# - Definitely more frameworky.  You couldn't successfully hand this code off 
#   to someone who was unwilling to learn about Pyramid security.  Trade-offs
#   are rampant when you outsource behavior to framework code.
#
# Extra:
#
# - Show PYRAMID_DEBUG_AUTHORIZATION

