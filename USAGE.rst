=====
Usage
=====


To develop on locationsharinglib:

.. code-block:: bash

    # The following commands require pipenv as a dependency

    # To lint the project
    _CI/scripts/lint.py

    # To execute the testing
    _CI/scripts/test.py

    # To create a graph of the package and dependency tree
    _CI/scripts/graph.py

    # To build a package of the project under the directory "dist/"
    _CI/scripts/build.py

    # To see the package version
    _CI/scipts/tag.py

    # To bump semantic versioning [--major|--minor|--patch]
    _CI/scipts/tag.py --major|--minor|--patch

    # To upload the project to a pypi repo if user and password are properly provided
    _CI/scripts/upload.py

    # To build the documentation of the project
    _CI/scripts/document.py


To use locationsharinglib in a project:

.. code-block:: python

    from locationsharinglib import Service
    cookies_file = 'FILE_CREATED_BY_MAPSCOOKIEGETTERCLI_AUTHENTICATION_PROCESS'
    google_email = 'username@gmail.com'
    service = Service(cookies_file=cookies_file, authenticating_account=google_email)
    for person in service.get_all_people():
        print(person)
