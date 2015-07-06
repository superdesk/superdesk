# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish import register_transmitter
from superdesk.publish.publish_service import PublishService
from superdesk.errors import PublishODBCError
import superdesk

try:
    import pyodbc

    pyodbc_available = True
except ImportError:
    pyodbc_available = False

errors = [PublishODBCError.odbcError().get_error_description()]


class ODBCPublishService(PublishService):
    """
    ODBCPublishService
    """

    def _transmit(self, queue_item, subscriber):
        """
        Transmit the given formatted item to the configured ODBC output. Configuration must have connection string
        and the name of a stored procedure.
        """

        if not superdesk.app.config['ODBC_PUBLISH'] or not pyodbc_available:
            raise PublishODBCError()

        config = queue_item.get('destination', {}).get('config', {})

        try:
            with pyodbc.connect(config['connection_string']) as conn:
                item = queue_item['formatted_item']

                ret = self._CallStoredProc(conn, procName=config['stored_procedure'], paramDict=item)
                conn.commit()
            return ret
        except Exception as ex:
            raise PublishODBCError.odbcError(ex, config)

    def _CallStoredProc(self, conn, procName, paramDict):
        params = ''
        for p in paramDict:
            if paramDict[p]:
                params += ('@{}=N\'{}\', '.format(p, paramDict[p]))
        params = params[:-2]
        sql = """SET NOCOUNT ON;
             DECLARE @ret int
             EXEC @ret = %s %s
             SELECT @ret""" % (procName, params)
        resp = conn.execute(sql).fetchone()
        if resp is not None:
            return resp[0]
        else:
            return 1

if pyodbc_available:
    register_transmitter('ODBC', ODBCPublishService(), errors)
