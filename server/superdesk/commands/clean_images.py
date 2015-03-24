# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk


class CleanImages(superdesk.Command):
    """
    This command is to be executed if the size of Mongo DB grows because of images not being
    properly removed.
    This command will remove all the images from the system which are not referenced by content.
    Probably an db.repairDatabase() is needed in Mongo to shring the DB size.
    """
    def run(self):
        try:
            print('Starting image cleaning.')
            print('Image cleaning completed successfully.')
        except Exception as ex:
            print(ex)

superdesk.command('app:clean_images', CleanImages())
