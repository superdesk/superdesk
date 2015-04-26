# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from publicapi.prepopulate.service import prepopulate_data
import superdesk


class AppPrepopulateCommand(superdesk.Command):

    option_list = [
        superdesk.Option('--file', '-f', dest='prepopulate_file', default='app_prepopulate_data.json')
    ]

    def run(self, prepopulate_file):
        prepopulate_data(prepopulate_file)
        return 'OK'


superdesk.command('app:prepopulate', AppPrepopulateCommand())
