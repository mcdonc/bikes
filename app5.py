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
    config.add_route('login', 'login/{userid}')
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
# - This step is typically where people's brains start to steam.  It's
#   because we've added yet another layer of abstraction by using the
#   ACLAuthorizationPolicy.  This abstraction requires us to understand this
#   "root factory" thing and what the policy does with the "root" it produces.
#
# - The root object produced by the root factory is a "resource".  You can
#   think of a resource as a security context.  It's called "root" because it's
#   presumed that there will be some number of resources arranged in a tree
#   with the object produced by the root factory at the root of the resource
#   tree.  In the above application the root object has no children, so it's
#   the *only* resource that the system ever sees when the application is run.
#   More complex authorization requirements can make use of children.
#
# - Every authorization policy is passed a *context* argument to its
#   ``permits`` method.  This argument will be a resource.  Our
#   DumbAuthorizationPolicy ignored this argument.  The ACLAuthorizationPolicy
#   does not; it uses the values in the ``__acl__`` attribute of the resource
#   its passed to determine whether the user possesses the permission relative
#   to this view execution.
#
# - An ACL is an access control list.  It is a sequence of ACEs (access control
#   entries).  ``(Allow, Authenticated, 'edit')`` means Allow people who
#   possess the Authenticated principal (you can think of it as a group) to
#   edit.  Only users who are explicitly allowed a permission in an ACL (by
#   mention of their userid or any group they're in such as "Authenticated")
#   will be permitted to execute a view protected by that permission.
#
# - The benefit of all this indirection: we no longer own any imperative code
#   which does authorization or authentication.  Our application uses entirely
#   declarative stuff to protect view execution.  We only add ACLs and
#   permissions, and we have no conditions in our code.  Declarative code
#   requires less testing, and you can typically be surer of the result as long
#   as you understand the abstraction.
