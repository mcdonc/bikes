#!/usr/bin/env python
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.security import Allow, Authenticated, remember, forget
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
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

# [1]
class Resource(object):
    def __init__(self, name='', acl=None,
                 parent=None):
        self.children = {}
        self.__name__ = name
        self.__parent__ = parent
        if acl is not None:
            self.__acl__ = acl

    def add_subresource(self, name, acl=None):
        self.children[name] = Resource(
            name, acl=acl, parent=self
            )

    def __getitem__(self, name):
        return self.children[name]

    def __repr__(self):
        return '<Resource named %r at %s>' % (
            self.__name__, id(self)
            )

# [2]
def root_factory(request):
    root = Resource(
        '',
        acl=[(Allow, 'fred', 'delete')]
        )
    root.add_subresource(
        '1',
        acl=[(Allow, Authenticated, 'delete')]
        )
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
    config.add_route('blogentry_delete', '/blog/{id}/delete',
                     traverse='/{id}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# New outcome: Fred can delete all blog entries.  Additionally, any
# authenticated user can delete blog entry named '1'.
#
# New features:
#
# [1] A Resource class.  It defines a __getitem__ that allows Pyramid to ask it
#     for a child.  Instances of Resource also get a __parent__ attribute which
#     point at the parent of a resource (another Resource).  Resource instances
#     may also have an ``__acl__``.
#
# [2] We use a function named root_factory to return the root object, which is
#     a Resource instance.  Before we return the root object, we give it a
#     single child named '1'.
#
# [3] We've added a ``traverse`` argument to the ``add_route`` call for the
#     ``blogentry_delete`` route.  This argument composes the security traversal
#     path for this view.  It uses the same pattern language as the route
#     pattern, so if the URL is ``/blog/1/delete``, the traversal path will
#     be ``/1``.
#
# Noteworthy:
#
# - We did not change our view code at all.  The changes we made were made to
#   the root factory and to the route associated ``blogentry_delete``.
#
# - Since we now have formed a security tree by returning an object that has
#   children from the root factory, and since the ``blogentry_delete`` route
#   now traverses the tree when it is matched, we can now protect individual
#   URLs differently from each other.
#
# - In the above application, ``/blog/1/delete`` can be executed by an
#   authenticated user, but ``/blog/2/delete`` cannot.  This is because the
#   effective ACL will allow the Authenticated user to delete as the result of
#   traversing to ``/1`` because there is such a node in the tree, but there
#   isn't any node in the security tree for ``/2`` so the root ACL is the only
#   ACL consulted.  This is often referred to as "object level security", and
#   is often a requirement for CMS-like systems.
#
# - Joe can delete 1 but not 2.
#
# - The ACLAuthorizationPolicy *inherits* ACLs from further down the tree
#   unless an explicit Deny is encountered.  This means that, since the root
#   resource has an __acl__ that says "Allow fred to delete", fred will have
#   the delete permission "everywhere" in the tree.  Unless fred (or another
#   principal possesed by the requesting user) is explicitly denied in an ACL
#   somewhere.
#
# - FYI, circref formed but not cleaned up when Resource instances are created
#   (a resource points to its parent using ``__parent__`` and the parent points
#   at its children via the ``children`` dictionary).
#
# - Note that in a real application, the resource tree would typically be
#   persisted somewhere (maybe in a database, or in a pickle), and not
#   recomposed on every request.

