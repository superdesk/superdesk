from apps.common.components.utils import get_component
from apps.legal_archive.components.legal_archive import LegalArchive
from superdesk import get_resource_service
from superdesk.celery_app import celery


@celery.task(bind=True, max_retries=3)
def update_legal_archive(self, ids):
    for _id in ids:
        archived_doc = get_resource_service('archive').find_one_in_base_backend(req=None, _id=_id)
        if not archived_doc:
            continue
        return get_component(LegalArchive).create([archived_doc])
