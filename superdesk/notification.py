"""Superdesk change notifications"""

import superdesk
import logging
from threading import Timer
from datetime import datetime
from eve.methods.common import parse, \
    store_media_files, resolve_user_restricted_access, resolve_sub_resource_path
from eve.defaults import resolve_default_values
from eve.utils import config
from eve.versioning import resolve_document_version, insert_versioning_documents
from cerberus.cerberus import ValidationError

log = logging.getLogger(__name__)

superdesk.domain('notification', {
    'schema': {
        'changes': {
            'type': 'dict',
            'allow_unknwon': True,
        }
    },
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
})

push_interval = 3
app = None
notifications = {}

def init_app(flask_app):
    global app, push_interval
    app = flask_app
    push_interval = app.config.get('NOTIFICATION_PUSH_INTERVAL', push_interval)
    Timer(push_interval, save_notification).start()

def save_notification():
    # TODO: pymongo connect
    global notifications, timer
    if notifications:
        old_notifications = notifications
        notifications = {}
        with app.test_request_context():
            log.info('Saving changes %s', old_notifications)
            post('notification', {'changes': old_notifications})
        
    Timer(push_interval, save_notification).start()

def push_notification(name, created=0, deleted=0, updated=0):
    log.info('Pushing for %s, created %s, deleted %s, updated %s', name, created, deleted, updated)
    if created == deleted == updated == 0: return
    
    changes = notifications.get(name)
    if changes == None:
        changes = notifications[name] = {
            'created': 0,
            'updated': 0,
            'deleted': 0
        }
        
    if created: changes['created'] += created
    if deleted: changes['deleted'] += deleted
    if updated: changes['updated'] += updated
    
def post(resource, payl):
    """ Adds one or more documents to a resource. Each document is validated
    against the domain schema. If validation passes the document is inserted
    and ID_FIELD, LAST_UPDATED and DATE_CREATED along with a link to the
    document are returned. If validation fails, a list of validation issues
    is returned.

    :param resource: name of the resource involved.
    :param payl: alternative payload. When calling post() from your own code
                 you can provide an alternative payload. This can be useful,
                 for example, when you have a callback function hooked to a
                 certain endpoint, and want to perform additional post() calls
                 from there.

                 Please be advised that in order to successfully use this
                 option, a request context must be available.

                 See https://github.com/nicolaiarocci/eve/issues/74 for a
                 discussion, and a typical use case.

    .. versionchanged:: 0.4
       Resolve default values before validation is performed. See #353.
       Support for document versioning.

    .. versionchanged:: 0.3
       Return 201 if at least one document has been successfully inserted.
       Fix #231 auth field not set if resource level authentication is set.
       Support for media fields.
       When IF_MATCH is disabled, no etag is included in the payload.
       Support for new validation format introduced with Cerberus v0.5.

    .. versionchanged:: 0.2
       Use the new STATUS setting.
       Use the new ISSUES setting.
       Raise 'on_pre_<method>' event.
       Explictly resolve default values instead of letting them be resolved
       by common.parse. This avoids a validation error when a read-only field
       also has a default value.
       Added ``on_inserted*`` events after the database insert

    .. versionchanged:: 0.1.1
       auth.request_auth_value is now used to store the auth_field value.

    .. versionchanged:: 0.1.0
       More robust handling of auth_field.
       Support for optional HATEOAS.

    .. versionchanged: 0.0.9
       Event hooks renamed to be more robuts and consistent: 'on_posting'
       renamed to 'on_insert'.
       You can now pass a pre-defined custom payload to the funcion.

    .. versionchanged:: 0.0.9
       Storing self.app.auth.userid in auth_field when 'user-restricted
       resource access' is enabled.

    .. versionchanged: 0.0.7
       Support for Rate-Limiting.
       Support for 'extra_response_fields'.

       'on_posting' and 'on_posting_<resource>' events are raised before the
       documents are inserted into the database. This allows callback functions
       to arbitrarily edit/update the documents being stored.

    .. versionchanged:: 0.0.6
       Support for bulk inserts.

       Please note: validation constraints are checked against the database,
       and not between the payload documents themselves. This causes an
       interesting corner case: in the event of a multiple documents payload
       where two or more documents carry the same value for a field where the
       'unique' constraint is set, the payload will validate successfully, as
       there are no duplicates in the database (yet). If this is an issue, the
       client can always send the documents once at a time for insertion, or
       validate locally before submitting the payload to the API.

    .. versionchanged:: 0.0.5
       Support for 'application/json' Content-Type .
       Support for 'user-restricted resource access'.

    .. versionchanged:: 0.0.4
       Added the ``requires_auth`` decorator.

    .. versionchanged:: 0.0.3
       JSON links. Superflous ``response`` container removed.
    """

    date_utc = datetime.utcnow().replace(microsecond=0)
    resource_def = app.config['DOMAIN'][resource]
    schema = resource_def['schema']
    validator = app.validator(schema, resource)
    documents = []
    issues = []

    if isinstance(payl, dict):
        payl = [payl]

    for value in payl:
        document = []
        doc_issues = {}
        try:
            document = parse(value, resource)
            resolve_default_values(document, resource_def['defaults'])
            validation = validator.validate(document)
            if validation:
                # validation is successful
                document[config.LAST_UPDATED] = \
                    document[config.DATE_CREATED] = date_utc

                resolve_user_restricted_access(document, resource)
                resolve_sub_resource_path(document, resource)
                store_media_files(document, resource)
                resolve_document_version(document, resource, 'POST')
            else:
                # validation errors added to list of document issues
                doc_issues = validator.errors
        except ValidationError as e:
            doc_issues['validation exception'] = str(e)
        except Exception as e:
            # most likely a problem with the incoming payload, report back to
            # the client as if it was a validation issue
            doc_issues['exception'] = str(e)

        issues.append(doc_issues)

        if len(doc_issues) == 0:
            documents.append(document)

    if len(documents):
        # notify callbacks
        getattr(app, "on_insert")(resource, documents)
        getattr(app, "on_insert_%s" % resource)(documents)

        # bulk insert
        ids = app.data.insert(resource, documents)

        # assign document ids
        for document in documents:
            # either return the custom ID_FIELD or the id returned by
            # data.insert().
            document[config.ID_FIELD] = \
                document.get(config.ID_FIELD, ids.pop(0))

        # insert versioning docs
        insert_versioning_documents(resource, documents)

        # notify callbacks
        getattr(app, "on_inserted")(resource, documents)
        getattr(app, "on_inserted_%s" % resource)(documents)
