import superdesk
from flask import request, Response, current_app as app
from superdesk.base_model import BaseModel
from superdesk.utils import get_random_string
from superdesk.emails import send_reset_password_email
from settings import RESET_PASSWORD_TOKEN_TIME_TO_LIVE as token_ttl
import logging
from .users import hash_password
from superdesk.utc import utcnow


logger = logging.getLogger(__name__)
bp = superdesk.Blueprint('reset_user_password', __name__)
superdesk.blueprint(bp)


@bp.route('/reset_user_password', methods=['POST'])
def reset_user_password():
    if not request.form:
        raise superdesk.SuperdeskError(payload='Invalid request.')

    email = request.form.get('email')
    key = request.form.get('token')
    password = request.form.get('password')

    active_tokens_model = ActiveTokensModel(app=app)
    reset_pass_model = ResetPasswordModel(app=app)
    if key and password:
        return update_password(key, password, active_tokens_model, reset_pass_model)

    if email:
        return initiate_reset_password(email, reset_pass_model)
    raise superdesk.SuperdeskError(payload='Invalid request')


def update_password(key, password, active_tokens_model, reset_password_model):
    reset_request = active_tokens_model.find_one(req=None, secret_key=key)
    if not reset_request:
        raise superdesk.SuperdeskError(payload='Invalid token received.')

    user_id = reset_request['user']
    user = app.data.find_one('users', req=None, _id=user_id)
    if not user:
        raise superdesk.SuperdeskError(payload='Invalid user.')

    updates = {}
    hashed = hash_password(password)
    updates['password'] = hashed
    updates[app.config['LAST_UPDATED']] = utcnow()
    superdesk.apps['users'].update(id=user_id, updates=updates, trigger_events=True)
    reset_password_model.delete(lookup={'email': reset_request['email']})
    return Response(status=200, response='Password updated')


def initiate_reset_password(email, reset_password_model):
    user = app.data.find_one('users', req=None, email=email)
    default_response = Response(response='Reset password initialized', status=201)
    if not user:
        logger.warning('User password reset triggered with invalid email: %s' % email)
        return default_response
    doc = {}
    doc['email'] = email
    doc[app.config['DATE_CREATED']] = utcnow()
    doc[app.config['LAST_UPDATED']] = utcnow()
    reset_password_model.create([doc])
    return default_response


reset_schema = {
    'email': {'type': 'email'},
    'secret_key': {'type': 'string'},
    'user': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'users',
            'field': '_id',
            'embeddable': True
        }
    }
}


class ActiveTokensModel(BaseModel):
    endpoint_name = 'active_tokens'
    internal_resource = True
    schema = reset_schema
    where_clause = '(ISODate() - this._created) / 3600000 <= %s' % token_ttl
    datasource = {
        'source': 'reset_password',
        'default_sort': [('_created', -1)],
        'filter': {'$where': where_clause}
    }
    resource_methods = []
    item_methods = []


class ResetPasswordModel(BaseModel):
    endpoint_name = 'reset_password'
    internal_resource = True
    schema = reset_schema
    resource_methods = []
    item_methods = []

    def create(self, docs, trigger_events=None, **kwargs):
        for doc in docs:
            email = doc.get('email')
            user = app.data.find_one('users', req=None, email=doc.get('email'))
            if not user:
                logger.warning('User password reset triggered with invalid email: %s' % email)
                raise superdesk.SuperdeskError(payload='Invalid request')
            doc['user'] = user['_id']
            doc['secret_key'] = get_random_string()
        ids = super().create(docs, trigger_events=False, **kwargs)
        for doc in docs:
            send_reset_password_email(doc)
        return ids
