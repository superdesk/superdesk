"""Superdesk IO"""

import superdesk
from superdesk.tokens import get_token
from .newsml import Parser
from .reuters import ReutersService

class UpdateIngest(superdesk.Command):
    """Update ingest feeds."""

    def run(self):
        db = superdesk.app.data
        ReutersService(Parser(), get_token(db), db).update()

superdesk.command('ingest:update', UpdateIngest())

superdesk.domain('feeds', {
    'schema': {
        'provider': {
            'type': 'string'
        }
    }
})
