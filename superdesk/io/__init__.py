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

superdesk.COMMANDS.update({
    'ingest:update': UpdateIngest()
})

superdesk.DOMAIN.update({
    'feeds': {
        'schema': {
            'provider': {
                'type': 'string'
            }
        }
    }
})
