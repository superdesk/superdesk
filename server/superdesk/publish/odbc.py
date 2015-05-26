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
from superdesk import get_resource_service
from superdesk.utc import utc
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

    def _transmit(self, formatted_item, subscriber, output_channel):
        """ Transmit the given formatted item to the configured ODBC output, configuration consists of the connection
         string and the name of a stored procedure
        :param formatted_item:
        :param subscriber:
        :param output_channel:
        :return:
        """
        if not superdesk.app.config['ODBC_PUBLISH'] or not pyodbc_available:
            raise PublishODBCError()

        config = output_channel.get('config', {})

        try:
            conn = pyodbc.connect(config['connection_string'])
            item = formatted_item['formatted_item']

            q_item = get_resource_service('publish_queue').find_one(req=None, formatted_item_id=formatted_item['_id'])
            item['publish_date'] = q_item['_created'].replace(tzinfo=utc).astimezone(tz=None).strftime(
                '%Y-%m-%d %H:%M:%S.%f')[:-3]

            ret = self._CallStoredProc(conn, procName=config['stored_procedure'], paramDict=item)
            conn.commit()
            conn.close()
            return ret
        except Exception as ex:
            raise PublishODBCError(ex, output_channel)

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
        return int(conn.execute(sql).fetchone()[0])

if pyodbc_available:
    register_transmitter('ODBC', ODBCPublishService(), errors)
