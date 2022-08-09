==================
locationsharinglib
==================

A library to retrieve coordinates from an google account that has been shared locations of other accounts.


* Documentation: https://locationsharinglib.readthedocs.org/en/latest


Install



.. code-block:: python

    pip install locationsharinglib


Usage:

.. code-block:: python

    from locationsharinglib import Service

    cookies_file = 'cookies.txt'
    google_email = '<your google username>@gmail.com'

    service = Service(cookies_file=cookies_file, authenticating_account=google_email)

    for person in service.get_all_people():
        print(person)



**cookies.txt file**

- You need to sign out, and manually sign into your Google account. Then browse to google.com/maps and extract from your "google.com" cookies and save it as `cookies.txt`
- Checkout `this chrome extension <https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid/related?hl=en>`_ to help export such file very easily
- Once `cookies.txt` created, if the Google account will be signed out it **will invalidate the cookies** 


Development Workflow
====================

The workflow supports the following steps

 * lint
 * test
 * build
 * document
 * upload
 * graph

These actions are supported out of the box by the corresponding scripts under _CI/scripts directory with sane defaults based on best practices.
Sourcing setup_aliases.ps1 for windows powershell or setup_aliases.sh in bash on Mac or Linux will provide with handy aliases for the shell of all those commands prepended with an underscore.

The bootstrap script creates a .venv directory inside the project directory hosting the virtual environment. It uses pipenv for that.
It is called by all other scripts before they do anything. So one could simple start by calling _lint and that would set up everything before it tried to actually lint the project

Once the code is ready to be delivered the _tag script should be called accepting one of three arguments, patch, minor, major following the semantic versioning scheme.
So for the initial delivery one would call

    $ _tag --minor

which would bump the version of the project to 0.1.0 tag it in git and do a push and also ask for the change and automagically update HISTORY.rst with the version and the change provided.


So the full workflow after git is initialized is:

 * repeat as necessary (of course it could be test - code - lint :) )
   * code
   * lint
   * test
 * commit and push
 * develop more through the code-lint-test cycle
 * tag (with the appropriate argument)
 * build
 * upload (if you want to host your package in pypi)
 * document (of course this could be run at any point)


Important Information
=====================

This template is based on pipenv. In order to be compatible with requirements.txt so the actual created package can be used by any part of the existing python ecosystem some hacks were needed.
So when building a package out of this **do not** simple call

    $ python setup.py sdist bdist_egg

**as this will produce an unusable artifact with files missing.**
Instead use the provided build and upload scripts that create all the necessary files in the artifact.



Project Features
================

* TODO
