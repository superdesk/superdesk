from collections import Counter
from eve.utils import ParsedRequest, config
from eve.validation import ValidationError
from superdesk import SuperdeskError, get_resource_service
from apps.archive import ArchiveService
from apps.content import LINKED_IN_PACKAGES
from apps.archive import ArchiveVersionsService
import logging

ASSOCIATIONS = 'refs'
ITEM_REF = 'residRef'
ID_REF = 'idRef'

logger = logging.getLogger(__name__)


class PackagesVersionsService(ArchiveVersionsService):

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get('archive_versions', req=req, lookup=lookup)


class PackageService(ArchiveService):

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get('packages', req=req, lookup=lookup)

    def on_create(self, docs):
        super().on_create(docs)
        self.check_package_associations(docs)

    def on_created(self, docs):
        super().on_created(docs)
        for (doc, assoc) in [(doc, assoc) for doc in docs
                             for assoc in self._get_associations(doc)]:
            self.update_link(doc[config.ID_FIELD], assoc)

    def on_update(self, updates, original):
        super().on_update(updates, original)
        associations = self._get_associations(updates)
        self.check_for_duplicates(original, associations)
        for assoc in associations:
            self.extract_default_association_data(original, assoc)

    def on_updated(self, updates, original):
        super().on_updated(updates, original)
        for assoc in self._get_associations(updates):
            self.update_link(original[config.ID_FIELD], assoc)

    def on_deleted(self, doc):
        super().on_deleted(doc)
        for assoc in self._get_associations(doc):
            self.update_link(doc[config.ID_FIELD], assoc, delete=True)

    def check_package_associations(self, docs):
        for (doc, group) in [(doc, group) for doc in docs for group in doc.get('groups', [])]:
            associations = group.get(ASSOCIATIONS, [])

            self.check_for_duplicates(doc, associations)
            for assoc in associations:
                self.extract_default_association_data(group, assoc)

    def extract_default_association_data(self, package, assoc):
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc)
        self.check_for_circular_reference(package, item_id)
        assoc['guid'] = item.get('guid', item_id)
        assoc['type'] = item.get('type')

    def get_associated_item(self, assoc):
        endpoint = assoc.get('location', 'archive')
        item_id = assoc[ITEM_REF]
        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)
        if not item:
            message = 'Invalid item reference: ' + assoc['itemRef']
            logger.error(message)
            raise SuperdeskError(message=message)
        return item, item_id, endpoint

    def update_link(self, package_id, assoc, delete=False):
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc)
        two_way_links = [d for d in item.get(LINKED_IN_PACKAGES, []) if not d['package'] == package_id]

        if not delete:
            two_way_links.append({'package': package_id})

        updates = {LINKED_IN_PACKAGES: two_way_links}
        get_resource_service(endpoint).patch(item_id, updates)

    def check_for_duplicates(self, package, associations):
        counter = Counter()
        package_id = package[config.ID_FIELD]
        for itemRef in [assoc[ITEM_REF] for assoc in associations if assoc.get(ITEM_REF)]:
            if itemRef == package_id:
                message = 'Trying to self reference as an association.'
                logger.error(message)
                raise SuperdeskError(message=message)
            counter[itemRef] += 1

        if any(itemRef for itemRef, value in counter.items() if value > 1):
            message = 'Content associated multiple times'
            logger.error(message)
            raise SuperdeskError(message=message)

    def check_for_circular_reference(self, package, item_id):
        if any(d for d in package.get(LINKED_IN_PACKAGES, []) if d['package'] == item_id):
            message = 'Trying to create a circular reference to: ' + item_id
            logger.error(message)
            raise ValidationError(message)

    def _get_associations(self, doc):
        return [assoc for group in doc.get('groups', [])
                for assoc in group.get(ASSOCIATIONS, [])]
