# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""
A module that runs the Superdesk public API.

The API is built using the `Eve framework <http://python-eve.org/>`_ and is
thus essentially just a normal `Flask <http://flask.pocoo.org/>`_ application.

.. note:: The public API should not be confused with the "internal" API that
    is meant to be used by the Superdesk browser client only.
"""


from publicapi import get_app


if __name__ == '__main__':
    app = get_app()
    app.run(
        host='0.0.0.0',
        port=5050,   # XXX: have PUBAPI_PORT in config... and other things
        debug=True,  # TODO: remove before pushing to production (+ have in cfg)
        use_reloader=True
    )
