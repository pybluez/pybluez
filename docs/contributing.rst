=======================
Contributing to PyBluez
=======================


**This project is not currently under active development**. 

Contributions are strongly desired to resolve compatibility problems on newer systems, address bugs, and improve platform support for 
various features. Here are some guidelines to follow.

Compatibility Issues
====================

Please submit compatiblity issues by opening an `issue`_ explaining the problem clearly
and providing information necessary to reproduce the issue, including sample
code and logs.

If you have long logs, please post them on https://gist.github.com and link to
the Gist in your issue.

Bugs
====

Please submit bug reports by opening an `issue`_ explaining the problem clearly
using code examples.

Coding
======

.. todo:: Develop PyBluez coding standards and style guides.

Documentation
=============

The documentation source lives in the `docs`_ folder. Contributions to the
documentation are welcome but should be easy to read and understand. 
All source documents are in restructured text format.

.. todo:: Develop PyBluez documentation standards and style guides.


Commit messages and pull requests
=================================

Commit messages should be concise but descriptive, and in the form of an instructional
patch description (e.g., "Add macOS support" not "Added macOS support").

Commits which close, or intend to close, an issue should include the phrase
"fix #234" or "close #234" where ``#234`` is the issue number, as well a short description,
for example: "Add logic to support Win10, fix #234". Pull requests should aim to match or closely match 
the corresponding issue title.


Copyrights
==========

By submitting to this project you agree to your code or documentation being
released under the projects :doc:`license <license>`. Copyrights on submissions are 
owned by their authors. Feel free to append your name to the list of contributors 
in :file:`contributors.rst` found in the projects `docs`_ folder as part of your pull request!



.. _docs: https://github.com/pybluez/pybluez/tree/master/docs
.. _issue: https://github.com/pybluez/pybluez/issues