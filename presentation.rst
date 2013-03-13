.. include:: <s5defs.txt>

Auth Is Hard, Let's Ride Bikes
==============================

:Authors: Chris McDonough, Agendaless Consulting
:Date: 2013/03/16 (PyCon 2013)

..  footer:: https://github.com/mcdonc/bikes

Talk Format
-----------

- Code-heavy talk.You're encouraged to obtain code samples by snagging them
  from https://github.com/mcdonc/bikes or just reading online from there.

- Evolve an application through no-security to too-much-security.

Principles
----------

- We'd like to be able to defer thinking about security at all in the initial
  stages of our project.

- Although it's less understandable than ad-hoc imperative code, for larger
  projects, making security mostly *declarative* is useful.

- Declarative stuff means fewer conditions; they are where bugs live.

Modes
-----

- "Global" security: "Fred can delete blog posts", "Authenticated users can
  delete blog posts".

- "Object-level" security: "Fred can delete *this* blog post, but not *that*
  blog post".  AKA "row-level security" in SQL-based systems.

Definitions
-----------

- Principal: a user or group.  Often a string.  A single "real" user is usually
  associated with several principals (e.g. Fred might be represented by "fred",
  "Authenticated", "Everyone", and "group:admins").

- Permission: a unique string representing an action.  "delete", "read",
  "edit", etc.

On To the Code
--------------

- We're going to just read code from here on in.

More Resources
--------------

- Michael Merickel's Pyramid Auth Demo:
  http://michael.merickel.org/projects/pyramid_auth_demo/
