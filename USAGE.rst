=====
Usage
=====

To use locationsharinglib in a project:

.. code-block:: python

    from locationsharinglib import Service
    service = Service(username, password)
    print(service.get_person_by_nickname('nick_name'))
