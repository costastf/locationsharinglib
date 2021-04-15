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
    cookies_file = 'COOKIE_RETRIEVED_BY_A_BROWSER_ADDON_LIKE_COOKIES.TXT_AFTER_MANUAL_LOGIN'
    google_email = 'username@gmail.com'
    service = Service(cookies_file=cookies_file, authenticating_account=google_email)
    for person in service.get_all_people():
        print(person)

    person = service.get_person_by_nickname(nickname)
    print(person)
    print(person.address)

    person = service.get_person_by_full_name(full_name)
    print(person)
    print(person.address)

    latitude, longitude = service.get_coordinates_by_nickname(nickname)
    print(latitude, longitude)

    # for more capabilities, please see
    # https://locationsharinglib.readthedocs.io/en/latest/locationsharinglib.html#module-locationsharinglib.locationsharinglib

