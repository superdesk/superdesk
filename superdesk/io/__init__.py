"""Superdesk IO"""

from superdesk import manager

@manager.command
def update_ingest():
    """Update ingest"""
    from .newsml import Parser
    from .reuters import ReutersService
    from .reuters_token import ReutersTokenProvider
    ReutersService(Parser(), ReutersTokenProvider()).update()
