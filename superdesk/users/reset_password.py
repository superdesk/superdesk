import superdesk
from flask import current_app as app
from superdesk.base_model import BaseModel
from superdesk.utils import get_random_string
from superdesk.emails.emails import send_reset_password_email


class EmailNotFoundError(superdesk.SuperdeskError):
    status_code = 400
    payload = {'email': 1}


class ResetPasswordModel(BaseModel):
    endpoint_name = 'reset_password'
    schema = {
        'email': {
            'type': 'email',
            'required': True
        },
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
    resource_methods = ['POST']
    item_methods = []
    public_methods = ['POST']

    def create(self, docs, trigger_events=None, **kwargs):
        for doc in docs:
            user = app.data.find_one('users', req=None, email=doc.get('email'))
            if not user:
                raise EmailNotFoundError()
            doc['user'] = user['_id']
            doc['secret_key'] = get_random_string()
        ids = super().create(docs, trigger_events=True, **kwargs)
        for doc in docs:
            send_reset_password_email(doc)
        return ids
