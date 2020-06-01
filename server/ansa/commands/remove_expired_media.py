
import superdesk

from datetime import datetime, timedelta
from ansa.remove_expired_media import remove_expired_media


class RemoveExpiredMediaCommand(superdesk.Command):

    option_list = (
        superdesk.Option('--days', dest='days', default=50),
        superdesk.Option('--skip', dest='skip', default=0),
        superdesk.Option('--limit', dest='limit', default=0),
        superdesk.Option('--dry-run', dest='dry', required=False, action='store_true'),
    )

    def run(self, days=None, skip=None, limit=None, dry=False):
        now = datetime.now()
        stop = now - timedelta(days=int(days))
        legal = superdesk.get_resource_service('legal_archive')
        cursor = legal.get_from_mongo(req=None, lookup={'versioncreated': {'$lte': stop}}) \
            .sort('_id') \
            .skip(int(skip)) \
            .limit(int(limit))

        archived_service = superdesk.get_resource_service('archived')

        i = 0
        for item in cursor:
            if item.get('associations') or item.get('renditions'):
                i += 1
                doc = item.copy()
                doc['item_id'] = item['_id']
                remove_expired_media(archived_service, doc, dry=dry)

        print('checked', i, 'items')
