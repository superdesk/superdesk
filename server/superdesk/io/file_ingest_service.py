# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.ingest_service import IngestService
from datetime import timedelta
import os
import shutil
from superdesk.utc import utcnow
from superdesk.errors import IngestFileError


class FileIngestService(IngestService):

    def move_file(self, filepath, filename, provider, success=True):
        """
        Move the files from the current directory to the _Processed directory in successful
        else _Error if unsuccessful. Creates _Processed and _Error directory within current directory
        """

        try:
            if not os.path.exists(os.path.join(filepath, "_PROCESSED/")):
                os.makedirs(os.path.join(filepath, "_PROCESSED/"))
            if not os.path.exists(os.path.join(filepath, "_ERROR/")):
                os.makedirs(os.path.join(filepath, "_ERROR/"))
        except Exception as ex:
            raise IngestFileError.folderCreateError(ex, provider)

        try:
            if success:
                shutil.copy2(os.path.join(filepath, filename), os.path.join(filepath, "_PROCESSED/"))
            else:
                shutil.copy2(os.path.join(filepath, filename), os.path.join(filepath, "_ERROR/"))
        except Exception as ex:
            raise IngestFileError.fileMoveError(ex, provider)
        finally:
            os.remove(os.path.join(filepath, filename))

    def is_latest_content(self, last_updated, provider_last_updated=None):
        """Parse file only if it's not older than provider last update -10m"""

        if not provider_last_updated:
            provider_last_updated = utcnow() - timedelta(days=7)

        return provider_last_updated - timedelta(minutes=10) < last_updated
